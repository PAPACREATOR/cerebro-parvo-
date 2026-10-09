"""Pre-execution human gate for the single approved natural verify route."""
import base64
from urllib.error import HTTPError

import pytest

from nexus.host import Host
from nexus.tests.test_reverse_flow import http


def payload(text="Verifica a integridade deste ficheiro.", raw=b"conteudo original", filename="prova.txt"):
    return {
        "text": text,
        "filename": filename,
        "attachment": base64.b64encode(raw).decode("ascii"),
    }


def confirm(prepared, value, confirmed=True):
    return {
        "ticket": prepared["ticket"],
        "confirmed": confirmed,
        **value,
    }


def assert_empty(root):
    for name in ("runs", "creative", "canonical"):
        assert not list((root / name).iterdir())


def test_natural_verify_is_only_proposed_then_explicitly_confirmed(tmp_path, monkeypatch):
    host = Host(tmp_path)
    calls = []

    def fake_start(request, session):
        host.authorize(session)
        calls.append(request)
        return {"run_id": "a" * 32}

    monkeypatch.setattr(host, "start", fake_start)
    value = payload()
    with http(host) as call:
        prepared = call("/api/prepare-run", value)
        assert calls == []
        assert_empty(tmp_path)
        assert prepared["process"] == "verify"
        assert prepared["filename"] == value["filename"]
        assert prepared["attachment_bytes"] == len(b"conteudo original")
        assert len(prepared["attachment_sha256"]) == 64

        started = call("/api/confirm-run", confirm(prepared, value))
        assert started["run_id"] == "a" * 32

    assert len(calls) == 1
    assert calls[0] == {"process": "verify", **value}


@pytest.mark.parametrize("value", [
    payload(text="Revê este ficheiro."),
    payload(text="Não verifiques a integridade deste ficheiro."),
    payload(text='Ele escreveu «verifica a integridade deste ficheiro»'),
    payload(text="Verifica a integridade deste ficheiro e pesquisa na web."),
    {"text": "Verifica a integridade deste ficheiro.", "filename": "", "attachment": ""},
    payload(raw=b"", filename="vazio.txt"),
    payload(filename="../fora.txt"),
])
def test_unmapped_ambiguous_or_invalid_natural_request_never_prepares_execution(tmp_path, value):
    host = Host(tmp_path)
    with http(host) as call:
        with pytest.raises(HTTPError) as error:
            call("/api/prepare-run", value)
        assert error.value.code == 403
        assert call("/api/runs") == []
    assert_empty(tmp_path)
    assert not host.busy.locked()


def test_edit_after_review_consumes_ticket_and_never_executes(tmp_path, monkeypatch):
    host = Host(tmp_path)
    monkeypatch.setattr(host, "start", lambda *_: pytest.fail("changed request must not execute"))
    original = payload()
    changed = payload(raw=b"outros bytes")
    with http(host) as call:
        prepared = call("/api/prepare-run", original)
        with pytest.raises(HTTPError):
            call("/api/confirm-run", confirm(prepared, changed))
        with pytest.raises(HTTPError):
            call("/api/confirm-run", confirm(prepared, original))
    assert_empty(tmp_path)


def test_reject_consumes_ticket_without_execution(tmp_path, monkeypatch):
    host = Host(tmp_path)
    monkeypatch.setattr(host, "start", lambda *_: pytest.fail("rejected request must not execute"))
    value = payload()
    with http(host) as call:
        prepared = call("/api/prepare-run", value)
        cancelled = call("/api/confirm-run", confirm(prepared, value, confirmed=False))
        assert cancelled == {"status": "CANCELLED"}
        with pytest.raises(HTTPError):
            call("/api/confirm-run", confirm(prepared, value))
    assert_empty(tmp_path)


def test_pre_execution_ticket_does_not_survive_server_restart(tmp_path, monkeypatch):
    first = Host(tmp_path)
    value = payload()
    with http(first) as call:
        prepared = call("/api/prepare-run", value)

    restarted = Host(tmp_path)
    monkeypatch.setattr(restarted, "start", lambda *_: pytest.fail("stale ticket must not execute"))
    with http(restarted) as call:
        with pytest.raises(HTTPError):
            call("/api/confirm-run", confirm(prepared, value))
    assert_empty(tmp_path)


def test_normal_folha_does_not_expose_process_radio_buttons():
    from nexus.contracts import ROOT

    html = (ROOT / "ui" / "index.html").read_text("utf-8")
    javascript = (ROOT / "ui" / "app.js").read_text("utf-8")
    assert 'name="process"' not in html
    assert "input[name=\"process\"]" not in javascript
    assert "/api/prepare-run" in javascript
    assert "/api/confirm-run" in javascript
