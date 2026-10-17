"""M6 gate: normal Folha/Host path, not diagnostic /api/run.

Selectively retained from the historical M6 lab because it tests the normal
user route and cancellation. No Host/Store/Kernel changes are imported.

The OpenNotebook HTTP peer is synthetic. These tests do NOT prove a real
OpenNotebook + SurrealDB + local-model deployment (O0-O8 remain separate).
Only Windows tests exercise the real confined Host subprocess.
"""
import base64
import hashlib
import os
import time
from urllib.error import HTTPError

import pytest

from nexus.host import Host
from nexus.tests.test_reverse_flow import http
from nexus.tests.test_open_notebook_kernel_e2e import (
    SOURCE, fake_open_notebook, write_config,
)


def proposal():
    return {
        "text": "& interpretar documento",
        "filename": "fonte.txt",
        "attachment": base64.b64encode(SOURCE.encode("utf-8")).decode("ascii"),
    }


def await_result(call, run_id, seconds=170):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        state = call("/api/runs/" + run_id)
        if state["status"] != "RUNNING":
            return state
        time.sleep(0.1)
    pytest.fail("Host did not finish within the bounded test deadline")


def test_interpret_preparation_and_cancellation_never_dispatch(tmp_path):
    host = Host(tmp_path)
    request = proposal()
    with http(host) as call:
        with pytest.raises(HTTPError) as direct:
            call("/api/run", {"process": "interpret", **request})
        assert direct.value.code == 403

        prepared = call("/api/prepare-run", request)
        assert prepared["process"] == "interpret"
        assert prepared["attachment_sha256"] == hashlib.sha256(
            SOURCE.encode("utf-8")
        ).hexdigest()
        assert call("/api/runs") == []
        assert call("/api/confirm-run", {
            "ticket": prepared["ticket"], "confirmed": False, **request
        }) == {"status": "CANCELLED"}
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **request
            })
        assert replay.value.code == 403
        assert call("/api/runs") == []

    for name in ("runs", "creative", "canonical"):
        assert not list((tmp_path / name).iterdir())


@pytest.mark.skipif(os.name != "nt", reason="Native Host confinement requires Windows")
def test_interpret_normal_folha_both_human_gates_and_restart(tmp_path):
    root = tmp_path / "nexus-data"
    root.mkdir()
    write_config(root)
    host = Host(root)
    request = proposal()

    with fake_open_notebook() as backend, http(host) as call:
        prepared = call("/api/prepare-run", request)
        assert prepared["process"] == "interpret"
        assert backend.calls == 0
        assert call("/api/runs") == []
        assert not list((root / "creative").iterdir())

        run_id = call("/api/confirm-run", {
            "ticket": prepared["ticket"], "confirmed": True, **request
        })["run_id"]
        state = await_result(call, run_id)
        assert state["status"] == "HUMAN_REQUIRED", state
        assert state["result"]["outcome"] == "candidate"
        assert backend.calls == 1
        assert SOURCE in state["content"]
        assert (root / "creative" / run_id / "content.md").read_bytes() == (
            state["content"].encode("utf-8")
        )
        assert not (root / "canonical" / run_id).exists()

        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **request
            })
        assert replay.value.code == 403
        assert backend.calls == 1

        ticket = call("/api/prepare", {"run_id": run_id})["ticket"]
        approved = call("/api/approve", {
            "run_id": run_id, "ticket": ticket, "confirmed": True
        })
        assert approved["status"] == "PASS"
        assert backend.calls == 1
        expected_content = call("/api/runs/" + run_id)["content"]

    # Backend is stopped. Recovery must use the persisted Nexus state.
    restored = Host(root)
    with http(restored) as call:
        final = call("/api/runs/" + run_id)
        assert final["status"] == "PASS"
        assert final["content"] == expected_content
        assert final["result"]["ai_calls"] == 1
    canonical = root / "canonical" / run_id
    assert (canonical / "content.md").read_bytes() == expected_content.encode("utf-8")
    assert (canonical / "approval.json").is_file()
    assert (canonical / "provenance.json").is_file()


@pytest.mark.skipif(os.name != "nt", reason="Native Host confinement requires Windows")
def test_interpret_wrong_quote_blocks_without_creative_or_canonical(tmp_path):
    root = tmp_path / "nexus-data"
    root.mkdir()
    write_config(root)
    host = Host(root)
    request = proposal()

    with fake_open_notebook("wrong-quote") as backend, http(host) as call:
        prepared = call("/api/prepare-run", request)
        assert backend.calls == 0
        run_id = call("/api/confirm-run", {
            "ticket": prepared["ticket"], "confirmed": True, **request
        })["run_id"]
        state = await_result(call, run_id)
        assert state["status"] in ("BLOCKED", "FAIL"), state
        assert backend.calls == 1
        assert not (root / "creative" / run_id).exists()
        assert not (root / "canonical" / run_id).exists()

    restored = Host(root)
    with http(restored) as call:
        final = call("/api/runs/" + run_id)
        assert final["status"] != "PASS"
        assert not (root / "canonical" / run_id).exists()
