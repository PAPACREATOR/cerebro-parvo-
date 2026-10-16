"""Writer PDF export is available only through exact Folha text and one-use human tickets.

No real Writer launches here; live Windows LPAC and PDF assertions are in
test_native_writer_route_real.py. These cases prove product HTTP authority.
"""
import base64
import hashlib
import io
import struct
import zipfile
from urllib.error import HTTPError

import pytest

from nexus.host import Host
from nexus.tests.test_reverse_flow import http


def doc():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        archive.writestr("content.xml", '<?xml version="1.0"?><office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"/>')
    return stream.getvalue()


def proposal(text="& converter para pdf", *, filename="original.odt", raw=None):
    content = doc() if raw is None else raw
    return {"text": text, "filename": filename,
            "attachment": base64.b64encode(content).decode("ascii")}


def unsupported_zip_compression():
    raw = bytearray(doc())
    # Change the same member's method in local and central directory headers.
    # zipfile.ZipFile can enumerate it but .read() raises NotImplementedError.
    local = raw.index(b"PK\x03\x04")
    central = raw.index(b"PK\x01\x02")
    struct.pack_into("<H", raw, local + 8, 99)
    struct.pack_into("<H", raw, central + 10, 99)
    return bytes(raw)


@pytest.mark.parametrize(("text", "expected"), (
    ("& converter para pdf", "convert_pdf"),
    ("& exportar manuscrito para pdf", "book"),
    ("converter para pdf", "convert_pdf"),
    ("exportar manuscrito para pdf", "book"),
))
def test_writer_requires_preexecution_human_ticket(tmp_path, monkeypatch, text, expected):
    host = Host(tmp_path)
    calls = []
    def capture(request, session):
        host.authorize(session)
        calls.append(request)
        return {"run_id": "a" * 32}
    monkeypatch.setattr(host, "start", capture)
    data = proposal(text)
    with http(host) as call:
        with pytest.raises(HTTPError) as forbidden:
            call("/api/run", {"process": expected, **data})
        assert forbidden.value.code == 403
        prepared = call("/api/prepare-run", data)
        assert prepared["process"] == expected
        assert prepared["attachment_bytes"] == len(doc())
        assert prepared["attachment_sha256"] != ""
        assert not calls
        assert call("/api/runs") == []
        approved = call("/api/confirm-run", {"ticket": prepared["ticket"],
                                            "confirmed": True, **data})
        assert approved["run_id"] == "a" * 32
        with pytest.raises(HTTPError) as replayed:
            call("/api/confirm-run", {"ticket": prepared["ticket"],
                                     "confirmed": True, **data})
        assert replayed.value.code == 403
    assert calls == [{"process": expected, **data}]
    for root in ("runs", "creative", "canonical"):
        assert not list((tmp_path / root).iterdir())


@pytest.mark.parametrize("data", (
    proposal("& converter para pdf e executa script"),
    proposal("& nao converter para pdf"),
    proposal("& exportar manuscrito para pdf e pesquisar na web"),
    proposal("& converter para pdf", filename="original.docx"),
    proposal("& converter para pdf", raw=b"not a document"),
    proposal("& converter para pdf", raw=unsupported_zip_compression()),
    proposal("& exportar manuscrito para pdf", filename="malicioso.txt"),
    {"text": "& converter para pdf", "filename": "", "attachment": ""},
))
def test_writer_ambiguous_or_invalid_document_never_gets_ticket(tmp_path, data):
    host = Host(tmp_path)
    with http(host) as call:
        with pytest.raises(HTTPError) as refused:
            call("/api/prepare-run", data)
        assert refused.value.code == 403
        assert call("/api/runs") == []
    for root in ("runs", "creative", "canonical"):
        assert not list((tmp_path / root).iterdir())


@pytest.mark.parametrize("process", ("convert_pdf", "book"))
def test_edit_after_review_and_cancel_cannot_execute_writer(tmp_path, monkeypatch, process):
    host = Host(tmp_path)
    monkeypatch.setattr(host, "start", lambda *_: pytest.fail("Writer executed without a matching ticket"))
    data = proposal("& converter para pdf" if process == "convert_pdf" else "& exportar manuscrito para pdf")
    with http(host) as call:
        first = call("/api/prepare-run", data)
        altered = {**data, "text": data["text"] + " agora"}
        with pytest.raises(HTTPError):
            call("/api/confirm-run", {"ticket": first["ticket"],
                                      "confirmed": True, **altered})
        with pytest.raises(HTTPError):
            call("/api/confirm-run", {"ticket": first["ticket"],
                                      "confirmed": True, **data})
        second = call("/api/prepare-run", data)
        assert call("/api/confirm-run", {"ticket": second["ticket"],
                                         "confirmed": False, **data}) == {"status": "CANCELLED"}
        with pytest.raises(HTTPError):
            call("/api/confirm-run", {"ticket": second["ticket"],
                                      "confirmed": True, **data})
        assert call("/api/runs") == []
    for root in ("runs", "creative", "canonical"):
        assert not list((tmp_path / root).iterdir())


@pytest.mark.parametrize("text", [
    "Verifica este documento e converte-o em PDF",
    "& verificar integridade de ficheiro e converter para pdf",
])
def test_composed_pdf_proposal_is_read_only_and_does_not_bypass_host_gates(tmp_path, text):
    host = Host(tmp_path)
    with http(host) as call:
        advice = call("/api/interpret", {"text": text})
        assert advice["execution"] == "NOT_AUTHORIZED"
        assert advice["composite"]["authority"] == "NONE"
        assert advice["composite"]["execution"] == "NOT_AUTHORIZED"
        assert advice["composite"]["requires_human_confirmation"] is True
        assert [step["process"] for step in advice["composite"]["steps"]] == ["verify", "convert_pdf"]
        with pytest.raises(HTTPError):
            call("/api/prepare-run", proposal(text=text))
        assert call("/api/runs") == []
    assert not list((tmp_path / "creative").iterdir())
    assert not list((tmp_path / "canonical").iterdir())


@pytest.mark.parametrize("text", [
    "Não verifica este documento e converte-o em PDF",
    "Verifica este documento e converte-o em PDF e publica-o",
    "O título é: verifica este documento e converte-o em PDF",
    "Verifica este documento ou converte-o em PDF",
])
def test_composed_pdf_negation_quotes_and_ambiguity_never_create_plan(tmp_path, text):
    host = Host(tmp_path)
    with http(host) as call:
        preview = call("/api/interpret", {"text": text})
        assert "composite" not in preview
        assert call("/api/runs") == []


def test_composed_receipt_does_not_invent_history_or_execute_tools(tmp_path, monkeypatch):
    host = Host(tmp_path)
    def forbidden(*_args, **_kwargs):
        pytest.fail("Read-only receipt tried to execute a tool")
    monkeypatch.setattr(host, "start", forbidden)
    request = {
        "text": "Verifica este documento e converte-o em PDF",
        "filename": "original.odt", "input_sha256": "a" * 64,
        "verify_run_id": "b" * 32, "convert_run_id": "c" * 32,
    }
    with http(host) as call:
        for altered in (
            request,
            {**request, "convert_run_id": request["verify_run_id"]},
            {**request, "input_sha256": "not-a-hash"},
            {**request, "text": "Não verifica este documento e converte-o em PDF"},
            {**request, "filename": "../original.odt"},
            {**request, "verify_run_id": "../../etc/passwd"},
            {**request, "unexpected": "field"},
        ):
            with pytest.raises(HTTPError) as denied:
                call("/api/flow-receipt", altered)
            assert denied.value.code == 403
        with pytest.raises(HTTPError) as other_session:
            call("/api/flow-receipt", request, session="not-the-host-session")
        assert other_session.value.code == 403
        assert call("/api/runs") == []
    assert not list((tmp_path / "creative").iterdir())
    assert not list((tmp_path / "canonical").iterdir())


def test_two_independent_folha_drafts_survive_host_restart(tmp_path):
    import base64
    import hashlib
    from nexus.tests.test_reverse_flow import http
    folder = tmp_path / "runtime"
    host = Host(folder)
    raw = bytes(range(256)) * 5 + "Oliveira do Hospital".encode("utf-8")
    payload = {
        "slot": "a", "expected_revision": 0,
        "text": "Verifica este documento depois", "filename": "documento_ação.bin",
        "attachment": base64.b64encode(raw).decode("ascii"),
    }
    with http(host) as call:
        assert call("/api/folha-draft/a")["revision"] == 0
        first = call("/api/folha-draft", payload)
        assert first["revision"] == 1
        assert first["input_sha256"] == hashlib.sha256(raw).hexdigest()
        other = call("/api/folha-draft", {
            "slot": "b", "expected_revision": 0,
            "text": "Outra Folha para estudar", "filename": "", "attachment": "",
        })
        assert other["revision"] == 1
        assert call("/api/runs") == []
        with pytest.raises(HTTPError) as lost_update:
            call("/api/folha-draft", payload)
        assert lost_update.value.code == 403
        with pytest.raises(HTTPError) as not_owner:
            call("/api/folha-draft/a", session="other-session")
        assert not_owner.value.code == 403
    # Host session changes at restart but durable local scratch is recoverable
    # through the NEW session only. No external tool was invoked.
    restored = Host(folder)
    with http(restored) as call:
        loaded = call("/api/folha-draft/a")
        assert loaded["text"] == payload["text"]
        assert loaded["filename"] == payload["filename"]
        assert base64.b64decode(loaded["attachment"], validate=True) == raw
        assert loaded["revision"] == 1
        assert call("/api/folha-draft/b")["text"] == "Outra Folha para estudar"
        assert call("/api/runs") == []
    for area in ("runs", "creative", "canonical"):
        assert not list((folder / area).iterdir())


@pytest.mark.parametrize("change", [
    {"slot": "c", "expected_revision": 0, "text": "ok", "filename": "", "attachment": ""},
    {"slot": "../a", "expected_revision": 0, "text": "ok", "filename": "", "attachment": ""},
    {"slot": "a", "expected_revision": True, "text": "ok", "filename": "", "attachment": ""},
    {"slot": "a", "expected_revision": 0, "text": "ok", "filename": "x.bin", "attachment": ""},
    {"slot": "a", "expected_revision": 0, "text": "ok", "filename": "", "attachment": "YWJj"},
    {"slot": "a", "expected_revision": 0, "text": "ok", "filename": "sub/file", "attachment": "YWJj"},
    {"slot": "a", "expected_revision": 0, "text": "ok", "filename": "data.bin", "attachment": "**invalid**"},
    {"slot": "a", "expected_revision": 0, "text": "x" * 12001, "filename": "", "attachment": ""},
])
def test_folha_draft_refuses_invalid_data_without_execution(tmp_path, change):
    host = Host(tmp_path / "runtime")
    with http(host) as call:
        with pytest.raises(HTTPError) as rejected:
            call("/api/folha-draft", change)
        assert rejected.value.code == 403
        assert call("/api/runs") == []


def test_corrupted_folha_draft_blocks_restoration_without_repair_or_execution(tmp_path):
    import json
    host = Host(tmp_path / "runtime")
    with http(host) as call:
        call("/api/folha-draft", {
            "slot": "a", "expected_revision": 0,
            "text": "Original", "filename": "", "attachment": "",
        })
    saved = tmp_path / "runtime-folha-drafts" / "a.json"
    corrupt = json.loads(saved.read_bytes())
    corrupt["text"] = "Adulterado"
    saved.write_text(json.dumps(corrupt), encoding="utf-8")
    preserved = saved.read_bytes()
    with http(Host(tmp_path / "runtime")) as call:
        with pytest.raises(HTTPError) as refused:
            call("/api/folha-draft/a")
        assert refused.value.code == 403
        assert call("/api/runs") == []
    assert saved.read_bytes() == preserved


@pytest.mark.parametrize("with_attachment", [False, True])
def test_pending_human_clarification_survives_restart_without_running_tools(tmp_path, with_attachment):
    folder = tmp_path / "runtime"
    original = "Cria um podcast sobre Guimarães"
    question = "Que tom pretendes e quanto deve durar?"
    draft = {"slot": "a", "expected_revision": 0, "text": "Informal, 5",
             "filename": "", "attachment": "",
             "dialogue": {"original": original, "question": question}}
    binary = bytes([0, 1, 2, 10, 13, 255, 128, 65, 0])
    if with_attachment:
        draft.update(filename="ação.bin", attachment=base64.b64encode(binary).decode("ascii"))
    with http(Host(folder)) as call:
        saved = call("/api/folha-draft", draft)
        assert saved["dialogue"] == draft["dialogue"]
        assert call("/api/runs") == []
    with http(Host(folder)) as call:
        resumed = call("/api/folha-draft/a")
        assert resumed["text"] == "Informal, 5"
        assert resumed["dialogue"] == draft["dialogue"]
        assert resumed["revision"] == 1
        assert resumed["filename"] == draft["filename"]
        assert resumed["attachment"] == draft["attachment"]
        if with_attachment:
            assert base64.b64decode(resumed["attachment"]) == binary
            assert resumed["input_sha256"] == hashlib.sha256(binary).hexdigest()
        assert call("/api/runs") == []
    for area in ("runs", "creative", "canonical"):
        assert not list((folder / area).iterdir())


@pytest.mark.parametrize("invalid", [
    {"original": "", "question": "Qual o tom?"},
    {"original": "Pedido", "question": ""},
    {"original": "Pedido", "question": "Pergunta", "ticket": "secret"},
    {"original": "Pedido", "question": "?" * 251},
    ["Pedido", "Pergunta"],
    "texto",
    True,
])
def test_dialogue_scratch_rejects_invalid_authority_fields(tmp_path, invalid):
    with http(Host(tmp_path / "runtime")) as call:
        with pytest.raises(HTTPError) as refused:
            call("/api/folha-draft", {
                "slot": "a", "expected_revision": 0, "text": "Resposta",
                "filename": "", "attachment": "", "dialogue": invalid,
            })
        assert refused.value.code == 403
        assert call("/api/runs") == []


def test_dialogue_draft_tampering_is_rejected_without_side_effects(tmp_path):
    import json
    folder = tmp_path / "runtime"
    with http(Host(folder)) as call:
        call("/api/folha-draft", {
            "slot": "a", "expected_revision": 0, "text": "5 minutos",
            "filename": "", "attachment": "",
            "dialogue": {"original": "Cria um podcast", "question": "Que tom?"},
        })
    target = tmp_path / "runtime-folha-drafts" / "a.json"
    contents = json.loads(target.read_text("utf-8"))
    contents["dialogue"]["original"] = "Pedido falsificado"
    target.write_text(json.dumps(contents), encoding="utf-8")
    with http(Host(folder)) as call:
        with pytest.raises(HTTPError) as refused:
            call("/api/folha-draft/a")
        assert refused.value.code == 403
        assert call("/api/runs") == []
