"""Molde v1: read-only universal input view, not an authority or Store clone."""
import base64
import hashlib
import json

import pytest
from urllib.error import HTTPError

from nexus.adapters.constitutional import build_molde
from nexus.contracts import Blocked
from nexus.host import Host
from nexus.tests.test_reverse_flow import http


def payload(raw):
    return base64.b64encode(raw).decode("ascii")


@pytest.mark.parametrize(("name", "raw", "family"), [
    ("fonte.md", b"---\ntitulo: Amostra\n---\nTexto", "document"),
    ("livro.odt", b"ODT-binary-not-trusted", "document"),
    ("imagem.png", b"\x89PNG\r\n\x1a\nopaque", "image"),
    ("voz.wav", b"RIFFopaque", "audio"),
    ("curta.mp4", b"ftypopaque", "video"),
    ("incerto.xyz", b"\x00\xff\x7f", "unknown"),
    ("NOTA.TXT", "ação e memória 日本語".encode("utf-8"), "document"),
])
def test_any_file_gets_non_authoritative_mold(name, raw, family):
    envelope = build_molde("& transformar fonte", name, payload(raw), intent="trabalhar")
    assert envelope["schema"] == "nexus.molde.v1"
    assert envelope["source"] == {
        "channel": "folha", "kind": "file", "filename": name,
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
    }
    assert envelope["identity"]["id"] == "sha256:" + hashlib.sha256(raw).hexdigest()
    assert envelope["identity"]["version"] == 1
    assert envelope["classification"]["family"] == family
    assert envelope["classification"]["basis"] == "untrusted_filename_hint"
    assert envelope["process"]["authority"] == "NONE"
    assert envelope["relations"] == []
    assert envelope["record"] is None
    assert envelope["rules"]["promotion"] == "HUMAN_APPROVAL"
    assert json.loads(json.dumps(envelope, ensure_ascii=False)) == envelope


@pytest.mark.parametrize("text", [
    "?? ação 日本語 ç", "  & guarda isto\nNão aproves  ", "% 7 + 9",
    "---\napproval: automatic\ncanonical: true\n---", "texto \t com espaços",
])
def test_text_exact_identity_and_no_implicit_authority(text):
    value = build_molde(text, intent="trabalhar", process="verify")
    assert value["source"]["kind"] == "text"
    assert value["source"]["sha256"] == hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert value["classification"]["family"] == "text"
    assert value["process"] == {"candidate": "verify", "authority": "NONE"}
    assert value["record"] is None


@pytest.mark.parametrize(("text", "filename", "attachment"), [
    ("", "", ""),
    ("texto", "ficheiro.txt", ""),
    ("texto", "", "YWI="),
    ("texto", "../escape.txt", "YWI="),
    ("texto", "pasta\\ficheiro.txt", "YWI="),
    ("texto", "C:/ficheiro.txt", "YWI="),
    ("texto", "ficheiro\n.txt", "YWI="),
    ("texto", "fonte.txt", "!invalid!"),
    ("x" * 100001, "", ""),
    ("texto", "a.txt", payload(b"z" * (2_097_152 + 1))),
])
def test_bad_file_text_and_sizes_fail_closed(text, filename, attachment):
    with pytest.raises(Blocked):
        build_molde(text, filename, attachment)


@pytest.mark.parametrize("kwargs", [
    {"text": None},
    {"text": "x", "intent": 5},
    {"text": "x", "process": {}},
    {"text": "x", "filename": 1},
])
def test_invalid_types_rejected(kwargs):
    with pytest.raises(Blocked):
        build_molde(**kwargs)


def test_folha_interpret_exposes_mold_without_creating_records(tmp_path):
    host = Host(tmp_path)
    original = "?? explica ação 日本語"
    with http(host) as call:
        value = call("/api/interpret", {"text": original})
        assert value["execution"] == "NOT_AUTHORIZED"
        assert value["molde"]["source"]["sha256"] == hashlib.sha256(
            original.encode("utf-8")).hexdigest()
        assert value["molde"]["process"]["authority"] == "NONE"
        assert value["molde"]["record"] is None
        assert call("/api/interpret", {"text": ""})["molde"] is None
        assert call("/api/runs") == []
    assert all(not list((tmp_path / n).iterdir()) for n in ("runs", "creative", "canonical"))


def test_folha_preexecution_binds_mold_to_exact_source_not_execution(tmp_path):
    host = Host(tmp_path)
    raw = "Documentação de origem".encode("utf-8")
    request = {"text": "@ preparar plano de pesquisa web",
               "filename": "origem.txt", "attachment": payload(raw)}
    with http(host) as call:
        preview = call("/api/prepare-run", request)
        mold = preview["molde"]
        assert mold["source"]["sha256"] == preview["attachment_sha256"]
        assert mold["process"]["candidate"] == preview["process"] == "web"
        assert mold["process"]["authority"] == "NONE"
        assert call("/api/runs") == []
        assert call("/api/confirm-run", {
            "ticket": preview["ticket"], "confirmed": False, **request,
        }) == {"status": "CANCELLED"}
        assert call("/api/runs") == []


def test_verified_run_uses_store_as_authority_not_mold(tmp_path):
    host = Host(tmp_path)
    raw = b"immutable-original-123"
    request = {"process": "verify", "text": "& verificar integridade de ficheiro",
               "filename": "input.bin", "attachment": payload(raw)}
    run_id = host.store.create(request)
    with http(host) as call:
        detail = call("/api/runs/" + run_id)
        mold = detail["molde"]
        assert mold["record"]["run_id"] == run_id
        assert mold["record"]["status"] == detail["status"] == "RUNNING"
        assert mold["source"]["sha256"] == detail["input_sha256"]
        assert mold["classification"]["intent"] == "trabalhar"
        assert mold["relations"] == []
        assert mold["record"]["process_version"] == detail["process_version"]
        assert detail["process_id"] == request["process"]
        assert not list((tmp_path / "canonical").iterdir())
        (tmp_path / "runs" / run_id / "input.bin").write_bytes(b"tampered")
        with pytest.raises(HTTPError) as rejected:
            call("/api/runs/" + run_id)
        assert rejected.value.code == 403


@pytest.mark.parametrize("bad", ["\ud800", "name\udfff"])
def test_unpaired_unicode_is_rejected_without_creating_a_mold(bad):
    with pytest.raises(Blocked):
        build_molde(bad)
    with pytest.raises(Blocked):
        build_molde("texto", bad + ".txt", payload(b"abc"))


def test_unpaired_unicode_is_http_refusal_not_server_crash(tmp_path):
    host = Host(tmp_path)
    with http(host) as call:
        with pytest.raises(HTTPError) as failed:
            call("/api/interpret", {"text": "Explica \ud800"})
        assert failed.value.code == 403
        assert call("/api/runs") == []
