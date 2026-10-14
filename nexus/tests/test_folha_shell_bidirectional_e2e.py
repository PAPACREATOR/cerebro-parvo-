"""Real product Folha -> Windows Shell -> confined tool -> Creative -> human Canonical -> Folha.

This test deliberately uses the normal two-confirmation HTTP route. Unlike the
diagnostic /api/run tests, it does not bypass the first human gate, intercept
Host.start, simulate the external tool, or change Host/Store/Kernel source.
It does not claim power-loss or physical-PC acceptance.
"""
import base64
import hashlib
import json
import os
import time
from urllib.error import HTTPError

import pytest

from nexus.capability_router import BUILTIN_CAPABILITIES
from nexus.host import Host
from nexus.tests.test_reverse_flow import http


pytestmark = pytest.mark.skipif(os.name != "nt", reason="Actual Shell/LPAC Host execution requires Windows")


@pytest.mark.parametrize(("raw", "name"), [
    ("Origem com ação e 日本語.\n".encode("utf-8"), "relatório_ação_日本語.txt"),
    (bytes(range(256)) * 4 + b"\x00\xff", "relatório_ação_日本語.bin"),
], ids=("unicode-text", "binary-all-bytes"))
def test_product_folha_real_bidirectional_shell_two_gates_and_restart(tmp_path, monkeypatch, raw, name):
    capability = next(item for item in BUILTIN_CAPABILITIES if item.process == "verify")
    payload = {
        "text": "& " + capability.command,
        "filename": name,
        "attachment": base64.b64encode(raw).decode("ascii"),
    }
    expected = hashlib.sha256(raw).hexdigest()
    host = Host(tmp_path)

    with http(host) as call:
        # Production mode cannot dispatch directly or silently promote knowledge.
        with pytest.raises(HTTPError) as forbidden:
            call("/api/run", {"process": "verify", **payload})
        assert forbidden.value.code == 403

        prepared = call("/api/prepare-run", payload)
        assert prepared["process"] == "verify"
        assert prepared["attachment_sha256"] == expected
        assert prepared["attachment_bytes"] == len(raw)
        assert call("/api/runs") == []

        # A changed input consumes its original ticket, without any execution.
        with pytest.raises(HTTPError) as changed:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True,
                **dict(payload, attachment=base64.b64encode(raw + b"changed").decode("ascii")),
            })
        assert changed.value.code == 403
        assert call("/api/runs") == []

        prepared = call("/api/prepare-run", payload)
        run_id = call("/api/confirm-run", {
            "ticket": prepared["ticket"], "confirmed": True, **payload
        })["run_id"]
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **payload
            })
        assert replay.value.code == 403

        deadline = time.monotonic() + 90
        state = call("/api/runs/" + run_id)
        while state["status"] == "RUNNING" and time.monotonic() < deadline:
            time.sleep(.1)
            state = call("/api/runs/" + run_id)
        assert state["status"] == "HUMAN_REQUIRED", state
        assert state["result"]["status"] == "PASS"
        assert state["result"]["ai_calls"] == 0
        assert len(call("/api/runs")) == 1
        assert not host.store.path("canonical", run_id).exists()

        original_path = host.store.path("runs", run_id) / "input.bin"
        assert original_path.read_bytes() == raw
        host.store.check_input(host.store.state(run_id))
        candidate = host.store.path("creative", run_id)
        original_result = state["result"]
        assert candidate.joinpath("content.md").read_bytes() == state["content"].encode("utf-8")

        # A review ticket does not itself grant Canonical authority.
        denied = call("/api/prepare", {"run_id": run_id})
        with pytest.raises(HTTPError) as not_approved:
            call("/api/approve", {
                "run_id": run_id, "ticket": denied["ticket"], "confirmed": False,
            })
        assert not_approved.value.code == 403
        assert not host.store.path("canonical", run_id).exists()

        approved_ticket = call("/api/prepare", {"run_id": run_id})
        approved = call("/api/approve", {
            "run_id": run_id, "ticket": approved_ticket["ticket"], "confirmed": True,
        })
        assert approved["status"] == "PASS"

    canonical = host.store.path("canonical", run_id)
    stored = host.store.state(run_id)
    host.store.check_commit(stored)
    provenance = json.loads((canonical / "provenance.json").read_bytes())
    assert provenance["input_references"] == [{
        "path": "runs/" + run_id + "/input.bin", "sha256": expected,
    }]
    for reference in provenance["input_references"] + provenance["output_references"]:
        path = tmp_path / reference["path"]
        assert path.resolve().is_relative_to(tmp_path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
    assert (canonical / "content.md").read_bytes() == (candidate / "content.md").read_bytes()
    assert provenance["human_approval"]["sha256"] == stored["candidate_sha256"]
    assert (host.store.path("runs", run_id) / "input.bin").read_bytes() == raw

    def never_run_again(*_args, **_kwargs):
        pytest.fail("Restart/reverse traversal must not execute Shell/LPAC a second time")

    monkeypatch.setattr("nexus.host.launch_confined", never_run_again)
    recovered = Host(tmp_path)
    with http(recovered) as call:
        restored = call("/api/runs/" + run_id)
        assert restored["status"] == "PASS"
        assert restored["result"] == original_result
        assert restored["content"].encode("utf-8") == (canonical / "content.md").read_bytes()
        assert restored["input_sha256"] == expected
        assert call("/api/runs")[0]["run_id"] == run_id
    recovered.store.check_commit(recovered.store.state(run_id))
    recovered.store.check_input(recovered.store.state(run_id))
