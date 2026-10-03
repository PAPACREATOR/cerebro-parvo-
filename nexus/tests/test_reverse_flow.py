"""Reverse lineage and return path; use disposable synthetic data only."""
import base64
import hashlib
import json
import os
import shutil
import threading
import time
from contextlib import contextmanager
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from nexus.app import make_server
from nexus.contracts import ROOT, Blocked
from nexus.host import Host
from nexus.store import HumanDecision, Store
from nexus.tests.test_store import candidate, request


@contextmanager
def http(host):
    server = make_server(host)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = "http://127.0.0.1:" + str(server.server_port)

    def call(path, value=None, session=None):
        headers = {"Content-Type": "application/json", "X-Nexus-Session": host.session if session is None else session}
        req = Request(base + path, headers=headers,
                      data=None if value is None else json.dumps(value).encode("utf-8"))
        with urlopen(req, timeout=15) as response:
            return json.loads(response.read())

    try:
        yield call
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def approve(store, run):
    return store.promote(run, HumanDecision("synthetic-decision", "test-human", run,
                                          store.state(run)["candidate_sha256"], "APPROVE"))


def edit_json(path, change):
    value = json.loads(path.read_bytes())
    change(value)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def damage(root, run, kind):
    source = root / "runs" / run
    creative = root / "creative" / run
    if kind == "changed-original":
        (source / "input.bin").write_bytes(b"different original")
    elif kind == "missing-original":
        (source / "input.bin").unlink()
    elif kind == "changed-request":
        edit_json(source / "request.json", lambda value: value.update(text="different request"))
    elif kind == "missing-request":
        (source / "request.json").unlink()
    elif kind == "changed-draft":
        (creative / "content.md").write_bytes(b"different draft")
    elif kind == "missing-draft":
        (creative / "content.md").unlink()
    elif kind == "changed-result":
        edit_json(creative / "result.json", lambda value: value["evidence"][0].update(value="different evidence"))
    elif kind == "missing-result":
        (creative / "result.json").unlink()
    elif kind == "wrong-source-path":
        edit_json(creative / "provenance.json", lambda value: value["input_references"][0].update(path="runs/" + "a" * 32 + "/input.bin"))
    elif kind == "wrong-source-hash":
        edit_json(creative / "provenance.json", lambda value: value["input_references"][0].update(sha256="0" * 64))
    elif kind == "wrong-process":
        edit_json(creative / "provenance.json", lambda value: value.update(process_id="interpret"))
    elif kind == "changed-trace":
        edit_json(creative / "provenance.json", lambda value: value.update(execution={"invented": True}))


DAMAGES = ["changed-original", "missing-original", "changed-request", "missing-request",
           "changed-draft", "missing-draft", "changed-result", "missing-result",
           "wrong-source-path", "wrong-source-hash", "wrong-process", "changed-trace"]


@pytest.mark.parametrize("kind", DAMAGES)
@pytest.mark.parametrize("stage", ["approval", "restart"])
def test_broken_reverse_chain_never_approves_or_recovers_as_pass(tmp_path, kind, stage):
    store = Store(tmp_path)
    run = candidate(store)
    if stage == "restart":
        approve(store, run)
    damage(tmp_path, run, kind)
    preserved = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*")
                 if p.is_file() and p.name != "state.json"}
    if stage == "approval":
        with pytest.raises(Blocked):
            approve(store, run)
        assert not store.path("canonical", run).exists()
    else:
        recovered = Store(tmp_path).state(run)
        assert recovered["status"] == "BLOCKED"
        assert recovered["commit_status"] == "RECOVERY_REQUIRED"
        assert store.path("canonical", run).exists()
    assert {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*")
            if p.is_file() and p.name != "state.json"} == preserved


@pytest.mark.parametrize("kind", ["wrong-source-path", "wrong-source-hash", "wrong-process", "changed-trace"])
def test_valid_json_canonical_provenance_tampering_blocks_restart(tmp_path, kind):
    store = Store(tmp_path)
    run = candidate(store)
    approve(store, run)
    path = store.path("canonical", run) / "provenance.json"
    if kind == "wrong-source-path":
        change = lambda value: value["input_references"][0].update(path="../outside")
    elif kind == "wrong-source-hash":
        change = lambda value: value["input_references"][0].update(sha256="0" * 64)
    elif kind == "wrong-process":
        change = lambda value: value.update(process_id="interpret")
    else:
        change = lambda value: value.update(execution={"invented": True})
    edit_json(path, change)
    preserved = path.read_bytes()
    recovered = Store(tmp_path).state(run)
    assert recovered["status"] == "BLOCKED"
    assert recovered["commit_status"] == "RECOVERY_REQUIRED"
    assert path.read_bytes() == preserved


def test_source_change_after_review_blocks_confirmation(tmp_path):
    host = Host(tmp_path)
    run = candidate(host.store)
    ticket = host.prepare_approval(run, host.session)["ticket"]
    damage(tmp_path, run, "changed-original")
    with pytest.raises(Blocked):
        host.approve(run, ticket, True, host.session)
    assert not host.store.path("canonical", run).exists()


@pytest.mark.parametrize("approved", [False, True])
def test_http_never_returns_stale_approved_or_reviewable_content(tmp_path, approved):
    host = Host(tmp_path)
    run = candidate(host.store)
    if approved:
        approve(host.store, run)
    damage(tmp_path, run, "changed-draft")
    with http(host) as call:
        assert call("/api/runs")[0]["status"] == "BLOCKED"
        with pytest.raises(HTTPError) as error:
            call("/api/runs/" + run)
        assert error.value.code == 403
        if not approved:
            with pytest.raises(HTTPError):
                call("/api/prepare", {"run_id": run})


def test_restart_returns_saved_result_without_reexecuting_provider(tmp_path, monkeypatch):
    host = Host(tmp_path)
    run = candidate(host.store)
    approve(host.store, run)
    expected = host.detail(run, host.session)
    old_session = host.session

    def forbidden(*args, **kwargs):
        pytest.fail("Reverse reading/recovery must never reexecute a provider")

    monkeypatch.setattr("nexus.host.subprocess.Popen", forbidden)
    restored = Host(tmp_path)
    with http(restored) as call:
        with pytest.raises(HTTPError):
            call("/api/runs/" + run, session=old_session)
        actual = call("/api/runs/" + run)
        assert actual["status"] == "PASS"
        assert actual["content"] == expected["content"]
        assert actual["result"] == expected["result"]
        assert call("/api/runs")[0]["run_id"] == run
        assert restored.tickets == {}
        with pytest.raises(HTTPError):
            call("/api/prepare", {"run_id": run})


def test_relocated_copy_preserves_reverse_chain_without_provider(tmp_path, monkeypatch):
    source = tmp_path / "source"
    store = Store(source)
    run = candidate(store)
    approve(store, run)
    preserved = {str(p.relative_to(source)): p.read_bytes() for p in source.rglob("*")
                 if p.is_file() and p.name != "state.json"}
    restored_root = tmp_path / "restored-ação"
    shutil.copytree(source, restored_root)

    def forbidden(*args, **kwargs):
        pytest.fail("Restoring a packet must not invoke a provider")

    monkeypatch.setattr("nexus.host.subprocess.Popen", forbidden)
    restored = Host(restored_root)
    with http(restored) as call:
        assert call("/api/runs/" + run)["status"] == "PASS"
    assert {str(p.relative_to(restored_root)): p.read_bytes() for p in restored_root.rglob("*")
            if p.is_file() and p.name != "state.json"} == preserved
    assert Store(source).state(run)["status"] == "PASS"


def test_legacy_packets_are_checked_without_inventing_old_hashes(tmp_path):
    store = Store(tmp_path)
    run = candidate(store)
    approve(store, run)
    path = store.path("runs", run) / "state.json"

    def legacy(value):
        for key in ("request_sha256", "result_sha256", "provenance_sha256"):
            value.pop(key)

    edit_json(path, legacy)
    state = Store(tmp_path).state(run)
    assert state["status"] == "PASS"
    assert not any(key in state for key in ("request_sha256", "result_sha256", "provenance_sha256"))
    damage(tmp_path, run, "wrong-source-path")
    assert Store(tmp_path).state(run)["status"] == "BLOCKED"


@pytest.mark.skipif(os.name != "nt", reason="Real Windows/.NET hash and Conductor required")
@pytest.mark.parametrize("mode", ["text", "binary-attachment"])
def test_real_windows_result_back_to_original_and_folha_after_restart(tmp_path, monkeypatch, mode):
    raw = "Ação, memória e proveniência 日本語.\n".encode("utf-8") if mode == "text" else bytes(range(256)) * 4
    payload = {**request(), "text": raw.decode("utf-8") if mode == "text" else "Verificar este anexo",
               "attachment": "" if mode == "text" else base64.b64encode(raw).decode("ascii"),
               "filename": "" if mode == "text" else "ação & $ ' ensaio.bin"}
    expected_hash = hashlib.sha256(raw).hexdigest()
    host = Host(tmp_path)
    with http(host) as call:
        run = call("/api/run", payload)["run_id"]
        deadline = time.monotonic() + 65
        state = call("/api/runs/" + run)
        while state["status"] == "RUNNING" and time.monotonic() < deadline:
            time.sleep(.1)
            state = call("/api/runs/" + run)
        assert state["status"] == "HUMAN_REQUIRED", state
        ticket = call("/api/prepare", {"run_id": run})["ticket"]
        assert call("/api/approve", {"run_id": run, "ticket": ticket, "confirmed": True})["status"] == "PASS"
    final = host.store.path("canonical", run)
    provenance = json.loads((final / "provenance.json").read_bytes())
    for reference in provenance["output_references"] + provenance["input_references"]:
        path = tmp_path / reference["path"]
        assert path.resolve().is_relative_to(tmp_path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
    source = tmp_path / provenance["input_references"][0]["path"]
    assert source.read_bytes() == raw
    assert provenance["process_id"] == payload["process"]
    assert json.loads((source.parent / "request.json").read_bytes()) == payload
    envelope = json.loads((source.parent / "execution.stdout.json").read_bytes())
    assert [item["value"] for item in envelope["result"]["evidence"]] == [expected_hash, expected_hash]
    assert provenance["execution"]["workflow_sha256"] == hashlib.sha256(
        (ROOT / "processes/verify.yaml").read_bytes()).hexdigest()
    assert provenance["human_approval"]["sha256"] == hashlib.sha256((final / "content.md").read_bytes()).hexdigest()
    assert envelope["result"]["ai_calls"] == 0

    def forbidden(*args, **kwargs):
        pytest.fail("Restored result must use saved evidence, never execute Conductor again")

    monkeypatch.setattr("nexus.host.subprocess.Popen", forbidden)
    restored = Host(tmp_path)
    with http(restored) as call:
        returned = call("/api/runs/" + run)
        assert returned["status"] == "PASS"
        assert returned["content"].encode("utf-8") == (final / "content.md").read_bytes()
        assert returned["result"] == envelope["result"]
        assert returned["input_sha256"] == expected_hash
        assert call("/api/runs")[0]["run_id"] == run
