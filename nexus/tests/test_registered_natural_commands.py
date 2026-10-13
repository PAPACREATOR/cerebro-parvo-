"""Registered natural commands reach the existing gates; no new execution path."""
import base64
import hashlib
from urllib.error import HTTPError

import pytest

from nexus.capability_router import BUILTIN_CAPABILITIES
from nexus.frontdoor import parse
from nexus.host import Host
from nexus.tests.test_reverse_flow import http
from nexus.tests.test_office import odt


SOURCE = "Fonte humana — original.\n".encode("utf-8")


def proposal(capability, text=None):
    document = capability.process in {"book", "convert_pdf"}
    raw = odt() if document else SOURCE
    return {"text": capability.command if text is None else text,
            "filename": "original.odt" if document else "fonte.txt",
            "attachment": base64.b64encode(raw).decode("ascii")}


def assert_empty(root):
    for name in ("runs", "creative", "canonical"):
        assert not list((root / name).iterdir()), name


def variant(command, mode):
    if mode == "upper":
        return command.upper()
    if mode == "spacing":
        return "  " + command.replace(" ", "\t  ") + "\n"
    if mode == "width":
        return "".join(chr(ord(c) + 0xFEE0) if 33 <= ord(c) <= 126 else c for c in command)
    return command


@pytest.mark.parametrize("capability", BUILTIN_CAPABILITIES, ids=lambda c: c.process)
@pytest.mark.parametrize("mode", ("plain", "upper", "spacing", "width"))
def test_all_registered_natural_commands_resolve_without_rewriting(capability, mode):
    text = variant(capability.command, mode)
    parsed = parse(text)
    assert parsed.status == "RESOLVED"
    assert parsed.intent == capability.intent
    assert parsed.explicit is False
    assert parsed.original == text
    assert parsed.content == text


@pytest.mark.parametrize("capability", BUILTIN_CAPABILITIES, ids=lambda c: c.process)
def test_read_only_registered_preview_is_not_execution_or_approval(tmp_path, capability):
    host = Host(tmp_path)
    with http(host) as call:
        preview = call("/api/interpret", {"text": capability.command})
        assert preview["status"] == "RESOLVED"
        assert preview["intent"] == capability.intent
        assert preview["original"] == capability.command
        assert preview.get("registered_command") is True
        assert preview["execution"] == "NOT_AUTHORIZED"
        assert preview["confirmation_required"] is False
        assert call("/api/runs") == []
    assert_empty(tmp_path)


@pytest.mark.parametrize("capability", BUILTIN_CAPABILITIES, ids=lambda c: c.process)
def test_every_natural_command_requires_confirmation_and_deny_consumes_ticket(tmp_path, capability):
    host = Host(tmp_path)
    data = proposal(capability)
    with http(host) as call:
        prepared = call("/api/prepare-run", data)
        assert prepared["process"] == capability.process
        assert prepared["filename"] == data["filename"]
        assert prepared["attachment_sha256"] == hashlib.sha256(base64.b64decode(data["attachment"])).hexdigest()
        assert call("/api/runs") == []
        assert call("/api/confirm-run", {
            "ticket": prepared["ticket"], "confirmed": False, **data,
        }) == {"status": "CANCELLED"}
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **data,
            })
        assert replay.value.code == 403
    assert_empty(tmp_path)


@pytest.mark.parametrize("capability", BUILTIN_CAPABILITIES, ids=lambda c: c.process)
def test_allow_dispatches_once_with_original_request_unit_only(tmp_path, monkeypatch, capability):
    host = Host(tmp_path)
    dispatched = []

    def capture(request, session):
        host.authorize(session)
        dispatched.append(request)
        return {"run_id": "a" * 32}

    monkeypatch.setattr(host, "start", capture)
    data = proposal(capability)
    with http(host) as call:
        with pytest.raises(HTTPError) as direct:
            call("/api/run", {"process": capability.process, **data})
        assert direct.value.code == 403
        prepared = call("/api/prepare-run", data)
        assert not dispatched
        assert call("/api/confirm-run", {
            "ticket": prepared["ticket"], "confirmed": True, **data,
        }) == {"run_id": "a" * 32}
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **data,
            })
        assert replay.value.code == 403
    assert dispatched == [{"process": capability.process, **data}]
    assert_empty(tmp_path)


@pytest.mark.parametrize("capability", BUILTIN_CAPABILITIES, ids=lambda c: c.process)
@pytest.mark.parametrize("field", ("text", "filename", "attachment"))
def test_editing_any_bound_field_revokes_the_natural_ticket(tmp_path, capability, field):
    host = Host(tmp_path)
    data = proposal(capability)
    changes = {
        "text": capability.command.upper(),
        "filename": "outra-" + data["filename"],
        "attachment": base64.b64encode(
            odt(("meta.xml", "<metadata>alterado</metadata>"))
            if capability.process in {"book", "convert_pdf"} else b"alterado"
        ).decode("ascii"),
    }
    with http(host) as call:
        prepared = call("/api/prepare-run", data)
        with pytest.raises(HTTPError) as changed:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True,
                **{**data, field: changes[field]},
            })
        assert changed.value.code == 403
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **data,
            })
        assert replay.value.code == 403
        assert call("/api/runs") == []
    assert_empty(tmp_path)


@pytest.mark.parametrize("capability", BUILTIN_CAPABILITIES, ids=lambda c: c.process)
@pytest.mark.parametrize("kind", ("negative", "suffix", "compound", "quoted", "wrong-prefix"))
def test_near_commands_do_not_gain_registered_authority(tmp_path, capability, kind):
    command = capability.command
    text = {
        "negative": "não " + command,
        "suffix": command + " agora",
        "compound": command + " e apagar os ficheiros",
        "quoted": '"' + command + '"',
        "wrong-prefix": ("& " if capability.intent == "web" else "?? ") + command,
    }[kind]
    host = Host(tmp_path)
    with http(host) as call:
        preview = call("/api/interpret", {"text": text})
        assert preview.get("registered_command", False) is False
        assert preview["execution"] == "NOT_AUTHORIZED"
        with pytest.raises(HTTPError) as refused:
            call("/api/prepare-run", proposal(capability, text))
        assert refused.value.code == 403
        assert call("/api/runs") == []
    assert_empty(tmp_path)
