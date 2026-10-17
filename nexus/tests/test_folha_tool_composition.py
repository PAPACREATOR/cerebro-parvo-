"""Bounded Folha recipes: real validators, synthetic Host/Store/HTTP boundary.

No tool runs, sockets, subprocesses, model, vault writes, H1 or H2 are used here.
The dedicated Windows native test covers the real two-tool route separately.
"""
import base64
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path

import pytest

from nexus import app as folha
from nexus.contracts import Blocked


SOURCE = "Um ezemplo em português. 😀\n".encode("utf-8")
INPUT_SHA = hashlib.sha256(SOURCE).hexdigest()
ORIGINAL = "Verifica este texto e revê o português"


def review_result():
    diagnostic = {"software": {"name": "LanguageTool", "version": "fixture-1"},
                  "warnings": {"incompleteResults": False}, "language": {"code": "pt-PT"},
                  "matches": [{"message": "Ortografia", "context": {"text": "Um ezemplo"},
                               "replacements": [{"value": "exemplo"}], "offset": 3, "length": 7}]}
    return {"status": "UNKNOWN", "outcome": "candidate", "title": "Revisão de português",
            "markdown": "Sugestões. O original não foi alterado.", "ai_calls": 0,
            "evidence": [{"capability": "languagetool.cli.pt-PT", "status": "UNKNOWN",
                          "value": json.dumps({"version": "fixture-1", "matches": 1,
                                               "diagnostic": diagnostic}, ensure_ascii=False)}]}


@pytest.mark.parametrize("text", [ORIGINAL,
    "Verifica a integridade deste texto e revê o português",
    "& verificar integridade de ficheiro e rever texto"])
def test_review_recipe_has_two_existing_steps_and_no_authority(text):
    plan = folha._composite_plan(text)
    assert [(step["process"], step["command"]) for step in plan["steps"]] == [
        ("verify", "verificar integridade de ficheiro"), ("proofread", "rever texto")]
    assert plan["authority"] == "NONE"
    assert plan["execution"] == "NOT_AUTHORIZED"
    assert plan["requires_human_confirmation"] is True


@pytest.mark.parametrize("text", ["Não " + ORIGINAL, "Ele disse: " + ORIGINAL,
    ORIGINAL + " e publica", ORIGINAL + " e executa script", "Verifica este texto ou revê o português"])
def test_denied_or_ambiguous_review_recipe_is_not_selected(text):
    assert folha._composite_plan(text) is None


@pytest.mark.parametrize("source", [b"\xff", b"", b" ", b"a\0b", ("x" * 6001).encode()])
def test_review_source_refuses_binary_empty_nul_or_over_limit(source):
    with pytest.raises(Blocked):
        folha._proofread_input(source)


def test_diagnostic_remains_unknown_and_does_not_change_unicode_source():
    before = bytes(SOURCE)
    comparison = folha._proofread_comparison(review_result(), SOURCE)
    assert comparison == {"input_sha256": INPUT_SHA, "original_preserved": True,
        "integrity": "PASS", "proofreading": "UNKNOWN", "alerts": 1, "text_correctness": "NOT_ESTABLISHED"}
    assert SOURCE == before
    assert folha._proofread_input(("😀" * 6000).encode()) == "😀" * 6000


@pytest.mark.parametrize("change", ["count", "bool-count", "version", "filename-only", "incomplete", "language", "PASS"])
def test_fabricated_or_incomplete_diagnostic_never_becomes_validated_review(change):
    result = review_result()
    metadata = json.loads(result["evidence"][0]["value"])
    if change == "count":
        metadata["matches"] = 0
    elif change == "bool-count":
        metadata["matches"] = True
    elif change == "version":
        metadata["version"] = "other"
    elif change == "filename-only":
        metadata["diagnostic"] = "languagetool-output.json"
    elif change == "incomplete":
        metadata["diagnostic"]["warnings"]["incompleteResults"] = True
    elif change == "language":
        metadata["diagnostic"]["language"]["code"] = "en-US"
    else:
        result["status"] = "PASS"
    result["evidence"][0]["value"] = json.dumps(metadata)
    with pytest.raises(Blocked):
        folha._proofread_comparison(result, SOURCE)


class SyntheticStore:
    def __init__(self, root):
        # The product HTTP server expects a Store root for disposable Folha drafts.
        # This fixture only exposes its location; receipt verification never writes.
        self.root = Path(root)
        self.checked = []
        self.requests = {run: {"process": process, "text": "& " + command, "filename": "texto.txt",
                               "attachment": base64.b64encode(SOURCE).decode("ascii")}
                         for run, process, command in (("a"*32, "verify", "verificar integridade de ficheiro"),
                                                       ("b"*32, "proofread", "rever texto"))}

    def checked_bytes(self, vault, run_id, name):
        assert (vault, name) == ("runs", "request.json")
        self.checked.append(run_id)
        return json.dumps(self.requests[run_id]).encode()


class SyntheticHost:
    def __init__(self, root):
        self.store = SyntheticStore(root)
        verify = {"status": "PASS", "outcome": "agreement", "title": "Integridade",
                  "markdown": "As duas verificações sintéticas concordam.", "ai_calls": 0,
                  "evidence": [{"capability": "fixture.hash", "status": "PASS", "value": INPUT_SHA}]}
        self.states = {run: {"run_id": run, "status": "HUMAN_REQUIRED", "process_id": process,
            "title": "texto.txt", "input_sha256": INPUT_SHA, "result": result,
            **{key: "c"*64 for key in ("request_sha256", "process_sha256", "result_sha256", "candidate_sha256")}}
            for run, process, result in (("a"*32, "verify", verify), ("b"*32, "proofread", review_result()))}

    def authorize(self, session):
        if session != "synthetic-session":
            raise Blocked("Fixture session rejected")

    def detail(self, run_id, session):
        self.authorize(session)
        return deepcopy(self.states[run_id])

    def start(self, *_args):
        pytest.fail("Receipt attempted to start a tool")

    def approve(self, *_args):
        pytest.fail("Receipt attempted Canonical promotion")


def receipt_call(monkeypatch, host, data):
    # Capture the actual handler without binding a socket or creating a Host.
    monkeypatch.setattr(folha, "NexusHTTPServer", lambda _address, handler: handler)
    handler_type = folha.make_server(host)
    handler = object.__new__(handler_type)
    raw = json.dumps(data).encode()
    handler.path = "/api/flow-receipt"
    handler.headers = {"Content-Type": "application/json", "Content-Length": str(len(raw))}
    handler.rfile = io.BytesIO(raw)
    handler.guard = lambda: "synthetic-session"
    replies = []
    handler.reply = lambda code, value: replies.append((code, value))
    handler.do_POST()
    assert len(replies) == 1
    return replies[0]


def receipt_request():
    return {"text": ORIGINAL, "filename": "texto.txt", "input_sha256": INPUT_SHA,
            "verify_run_id": "a"*32, "proofread_run_id": "b"*32}


def test_existing_receipt_checks_both_saved_requests_without_execution_or_approval(monkeypatch, tmp_path):
    host = SyntheticHost(tmp_path / "store")
    before = deepcopy(host.store.requests)
    status, receipt = receipt_call(monkeypatch, host, receipt_request())
    assert status == 200
    assert host.store.checked == ["a"*32, "b"*32]
    assert host.store.requests == before
    assert [step["process"] for step in receipt["steps"]] == ["verify", "proofread"]
    assert receipt["authority"] == "NONE" and receipt["execution"] == "NOT_AUTHORIZED"
    assert receipt["human_approval_required"] is True
    assert receipt["comparison"]["proofreading"] == "UNKNOWN"
    assert receipt["comparison"]["text_correctness"] == "NOT_ESTABLISHED"
    assert "product" not in receipt


@pytest.mark.parametrize("change", ["source", "input-hash", "operation", "verify-UNKNOWN", "same-run", "authority"])
def test_receipt_refuses_changed_source_operation_or_missing_prerequisite(monkeypatch, tmp_path, change):
    host, data = SyntheticHost(tmp_path / "store"), receipt_request()
    if change == "source":
        host.store.requests["b"*32]["attachment"] = base64.b64encode(b"changed").decode()
    elif change == "input-hash":
        host.states["b"*32]["input_sha256"] = "d"*64
    elif change == "operation":
        host.store.requests["b"*32]["text"] = "& interpretar documento"
    elif change == "verify-UNKNOWN":
        host.states["a"*32]["result"]["status"] = "UNKNOWN"
    elif change == "same-run":
        data["proofread_run_id"] = data["verify_run_id"]
    else:
        data["confirmed"] = True
    assert receipt_call(monkeypatch, host, data)[0] == 403
