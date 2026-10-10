"""Two registered tools through the SAME normal Folha/Host/Kernel gates.

A real Windows test exercises two distinct local tools (verify and the
deterministic web query-spec adapter); it does not claim live web retrieval.
"""
import base64
import hashlib
import os
import time
from urllib.error import HTTPError

import pytest

from nexus.host import Host
from nexus.tests.test_reverse_flow import http


def source(text, filename, raw):
    return {
        "text": text,
        "filename": filename,
        "attachment": base64.b64encode(raw).decode("ascii"),
    }


def approve_run(call, value):
    prepared = call("/api/prepare-run", value)
    assert prepared["attachment_bytes"] > 0
    assert prepared["attachment_sha256"]
    return call("/api/confirm-run", {"ticket": prepared["ticket"],
                                    "confirmed": True, **value})["run_id"]


def test_two_different_adapters_each_require_a_separate_human_ticket(tmp_path, monkeypatch):
    host = Host(tmp_path)
    calls = []

    def guarded_start(request, session):
        host.authorize(session)
        calls.append(request)
        return {"run_id": ("%032d" % len(calls))}

    monkeypatch.setattr(host, "start", guarded_start)
    check = source("& verifica a integridade deste ficheiro", "input.bin", b"original")
    search = source("@ preparar consulta web", "consulta.txt", b"Consulta: verificacao original")
    with http(host) as call:
        first = call("/api/prepare-run", check)
        denied = call("/api/confirm-run", {
            "ticket": first["ticket"], "confirmed": False, **check})
        assert denied == {"status": "CANCELLED"}
        assert not calls
        with pytest.raises(HTTPError):
            call("/api/confirm-run", {"ticket": first["ticket"], "confirmed": True, **check})
        assert not calls
        run1 = approve_run(call, check)
        assert len(calls) == 1 and calls[0]["process"] == "verify"
        second = call("/api/prepare-run", search)
        altered = {**search, "attachment": base64.b64encode(b"other bytes").decode("ascii")}
        with pytest.raises(HTTPError):
            call("/api/confirm-run", {"ticket": second["ticket"], "confirmed": True, **altered})
        assert len(calls) == 1
        run2 = approve_run(call, search)
        assert run1 != run2
        assert [c["process"] for c in calls] == ["verify", "web"]
        with pytest.raises(HTTPError):
            call("/api/run", {"process": "web", **search})
    for dirname in ("runs", "creative", "canonical"):
        assert not list((tmp_path / dirname).iterdir())


@pytest.mark.skipif(os.name != "nt", reason="Real native Sandbox/Host E2E needs Windows")
def test_e2e_two_different_tools_two_separate_creative_and_canonical_gates(tmp_path, monkeypatch):
    original = b"nexus original for two tools"
    host = Host(tmp_path)
    with http(host) as call:
        first = source("& verifica a integridade deste ficheiro", "source.bin", original)
        assert call("/api/runs") == []
        verify_id = approve_run(call, first)
        state1 = _await_candidate(call, verify_id)
        assert state1["status"] == "HUMAN_REQUIRED", state1
        assert (tmp_path / "runs" / verify_id / "input.bin").read_bytes() == original
        assert not (tmp_path / "canonical" / verify_id).exists()

        sha = hashlib.sha256(original).hexdigest()
        # The second task is based on the human-reviewed first result.
        # It DOES NOT automatically execute the second tool.
        second = source("@ preparar consulta web", "consulta.txt",
                        ("Consulta: procurar fontes para SHA-256 " + sha).encode("utf-8"))
        preview2 = call("/api/prepare-run", second)
        assert preview2["process"] == "web"
        assert len(call("/api/runs")) == 1
        assert not (tmp_path / "canonical" / verify_id).exists()
        # An explicit decision promotes the first candidate.
        decision1 = call("/api/prepare", {"run_id": verify_id})
        assert call("/api/approve", {
            "run_id": verify_id, "ticket": decision1["ticket"], "confirmed": True,
        })["status"] == "PASS"
        # A separate human confirmation is indispensable for tool two.
        web_id = call("/api/confirm-run", {
            "ticket": preview2["ticket"], "confirmed": True, **second,
        })["run_id"]
        assert web_id != verify_id
        state2 = _await_candidate(call, web_id)
        assert state2["status"] == "HUMAN_REQUIRED", state2
        assert state2["result"]["outcome"] == "candidate"
        assert sha in state2["result"]["markdown"]
        assert not (tmp_path / "canonical" / web_id).exists()
        decision2 = call("/api/prepare", {"run_id": web_id})
        assert call("/api/approve", {
            "run_id": web_id, "ticket": decision2["ticket"], "confirmed": True,
        })["status"] == "PASS"
        assert call("/api/runs/" + verify_id)["status"] == "PASS"
        assert call("/api/runs/" + web_id)["status"] == "PASS"
    assert (tmp_path / "canonical" / verify_id / "content.md").is_file()
    assert (tmp_path / "canonical" / web_id / "content.md").is_file()
    # Persisted results, reverse provenance and restart are read-only.
    def no_execution(*_args, **_kwargs):
        pytest.fail("Restart replayed a tool")
    monkeypatch.setattr("nexus.host.launch_confined", no_execution)
    restarted = Host(tmp_path)
    for run_id in (verify_id, web_id):
        restarted.store.check_commit(restarted.store.state(run_id))
        assert restarted.store.state(run_id)["status"] == "PASS"


def _await_candidate(call, run_id):
    deadline = time.monotonic() + 90
    state = call("/api/runs/" + run_id)
    while state["status"] == "RUNNING" and time.monotonic() < deadline:
        time.sleep(.15)
        state = call("/api/runs/" + run_id)
    return state
