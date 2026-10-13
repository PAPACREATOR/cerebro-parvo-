"""Registered natural commands reach the existing gates; no new execution path."""
import base64
import hashlib
import json
import os
import time
from urllib.error import HTTPError

import pytest

from nexus.capability_router import BUILTIN_CAPABILITIES, Capability, CapabilityRouter, declared_router
from nexus.contracts import Blocked
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


def test_pure_recognition_supports_n_declarations_without_permissions(tmp_path, monkeypatch):
    monkeypatch.setattr("nexus.contracts.load_policy", lambda: pytest.fail("Recognition read policy"))
    monkeypatch.setattr(Host, "start", lambda *_: pytest.fail("Recognition executed a tool"))
    values = tuple(Capability("future_" + str(n), "trabalhar", "tarefa numero " + str(n),
                              "future_tool_" + str(n)) for n in range(100))
    router = CapabilityRouter(values)
    for capability in values:
        assert router.recognise_command(capability.command.upper()) == capability
    assert router.recognise_command("tarefa numero 100") is None
    for capability in BUILTIN_CAPABILITIES:
        assert declared_router().recognise_command(capability.command) == capability
    assert not list(tmp_path.iterdir())


def test_matching_command_across_intents_is_refused_without_priority():
    router = CapabilityRouter((
        Capability("a", "trabalhar", "comando integral", "a_file"),
        Capability("b", "web", "COMANDO  INTEGRAL", "b_file"),
    ))
    with pytest.raises(Blocked):
        router.recognise_command("comando integral")


@pytest.mark.parametrize("text", ("", "nunca rever texto", "rever texto agora", '"rever texto"'))
def test_pure_recognition_does_not_select_substrings(text):
    assert declared_router().recognise_command(text) is None


def wait_result(call, run_id):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        state = call("/api/runs/" + run_id)
        if state["status"] != "RUNNING":
            return state
        time.sleep(0.1)
    raise AssertionError("Native task did not finish within its bounded deadline")


@pytest.mark.skipif(os.name != "nt", reason="Actual Host/LPAC/Job execution requires Windows")
def test_two_natural_functions_execute_and_return_without_notebook_dependency(tmp_path, monkeypatch):
    host = Host(tmp_path)
    completed = []
    with http(host) as call:
        for process in ("verify", "music"):
            capability = next(c for c in BUILTIN_CAPABILITIES if c.process == process)
            data = proposal(capability)
            if process == "music":
                music_source = "Tema: Identidade portuguesa\nLetra: A cidade canta e guarda a memoria.\nEstilo: Fado com jazz\n".encode("utf-8")
                data["attachment"] = base64.b64encode(music_source).decode("ascii")
            original = base64.b64decode(data["attachment"])
            cancelled = call("/api/prepare-run", data)
            assert call("/api/confirm-run", {
                "ticket": cancelled["ticket"], "confirmed": False, **data,
            }) == {"status": "CANCELLED"}
            assert len(call("/api/runs")) == len(completed)

            prepared = call("/api/prepare-run", data)
            run_id = call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **data,
            })["run_id"]
            state = wait_result(call, run_id)
            assert state["status"] == "HUMAN_REQUIRED", state
            assert state["process_id"] == process
            assert state["result"]["ai_calls"] == 0
            assert state["result"]["status"] == ("PASS" if process == "verify" else "UNKNOWN")
            assert not (tmp_path / "canonical" / run_id).exists()
            assert (tmp_path / "runs" / run_id / "input.bin").read_bytes() == original
            assert json.loads((tmp_path / "runs" / run_id / "request.json").read_bytes()) == {
                "process": process, **data,
            }
            content = state["content"].encode("utf-8")
            provenance = json.loads((tmp_path / "creative" / run_id / "provenance.json").read_bytes())
            assert provenance["process_id"] == process
            assert provenance["input_references"] == [{
                "path": "runs/" + run_id + "/input.bin", "sha256": hashlib.sha256(original).hexdigest(),
            }]
            assert provenance["output_references"] == [{
                "path": "creative/" + run_id + "/content.md", "sha256": hashlib.sha256(content).hexdigest(),
            }]
            assert provenance["execution"]["process_sha256"] == state["process_sha256"]
            assert provenance["execution"]["summary"]["agents_executed"] == [capability.tool]
            assert provenance["tools"] == [item["capability"] for item in state["result"]["evidence"]]
            if process == "music":
                # A real deterministic spec is not a generated audio product.
                assert state["result"].get("artifact") is None

            with pytest.raises(HTTPError) as replay:
                call("/api/confirm-run", {
                    "ticket": prepared["ticket"], "confirmed": True, **data,
                })
            assert replay.value.code == 403
            review = call("/api/prepare", {"run_id": run_id})
            with pytest.raises(HTTPError) as denied:
                call("/api/approve", {"run_id": run_id, "ticket": review["ticket"], "confirmed": False})
            assert denied.value.code == 403
            assert not (tmp_path / "canonical" / run_id).exists()
            with pytest.raises(HTTPError) as consumed:
                call("/api/approve", {"run_id": run_id, "ticket": review["ticket"], "confirmed": True})
            assert consumed.value.code == 403
            review = call("/api/prepare", {"run_id": run_id})
            assert call("/api/approve", {
                "run_id": run_id, "ticket": review["ticket"], "confirmed": True,
            })["status"] == "PASS"
            completed.append((run_id, original, content))

    def no_repeat(*_args, **_kwargs):
        pytest.fail("Recovery must not prepare or execute tools again")

    monkeypatch.setattr("nexus.adapters.runner.prepare_task", no_repeat)
    monkeypatch.setattr("nexus.host.launch_confined", no_repeat)
    restored = Host(tmp_path)
    with http(restored) as call:
        for run_id, original, content in completed:
            assert call("/api/runs/" + run_id)["status"] == "PASS"
            restored.store.check_commit(restored.store.state(run_id))
            assert (tmp_path / "runs" / run_id / "input.bin").read_bytes() == original
            assert (tmp_path / "canonical" / run_id / "content.md").read_bytes() == content
