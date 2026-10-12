"""Natural interpretation uses the existing two human gates and native Host.

The OpenNotebook peer is synthetic. Native Windows tests exercise the real
Host/LPAC/Job boundary, not OpenNotebook/SurrealDB/model installation.
"""
import base64
import hashlib
import json
import os
import time
from urllib.error import HTTPError

import pytest

from nexus.frontdoor import parse
from nexus.host import Host
from nexus.tests.test_open_notebook_kernel_e2e import (
    CONFIG, SOURCE, fake_open_notebook, write_config,
)
from nexus.tests.test_reverse_flow import http


NATURAL_COMMANDS = (
    "interpretar documento",
    "INTERPRETAR DOCUMENTO",
    "  Interpretar\t documento\n",
    "ｉｎｔｅｒｐｒｅｔａｒ ｄｏｃｕｍｅｎｔｏ",
)


def proposal(text="interpretar documento"):
    return {
        "text": text,
        "filename": "fonte.txt",
        "attachment": base64.b64encode(SOURCE.encode("utf-8")).decode("ascii"),
    }


def assert_empty(root):
    for name in ("runs", "creative", "canonical"):
        assert not list((root / name).iterdir()), name


def await_result(call, run_id):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        state = call("/api/runs/" + run_id)
        if state["status"] != "RUNNING":
            return state
        time.sleep(0.1)
    pytest.fail("The native test did not finish within its bounded deadline")


@pytest.mark.parametrize("text", NATURAL_COMMANDS)
def test_natural_interpretation_preserves_original_and_deny_consumes_ticket(tmp_path, text):
    parsed = parse(text)
    assert parsed.status == "RESOLVED"
    assert parsed.intent == "trabalhar"
    assert parsed.explicit is False
    assert parsed.original == text
    assert parsed.content == text

    host = Host(tmp_path)
    data = proposal(text)
    with http(host) as call:
        prepared = call("/api/prepare-run", data)
        assert prepared["process"] == "interpret"
        assert prepared["attachment_sha256"] == hashlib.sha256(
            SOURCE.encode("utf-8")
        ).hexdigest()
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


def test_natural_allow_dispatches_only_the_exact_confirmed_request(tmp_path, monkeypatch):
    host = Host(tmp_path)
    calls = []

    def capture(request, session):
        host.authorize(session)
        calls.append(request)
        return {"run_id": "a" * 32}

    monkeypatch.setattr(host, "start", capture)
    data = proposal(NATURAL_COMMANDS[2])
    with http(host) as call:
        with pytest.raises(HTTPError) as direct:
            call("/api/run", {"process": "interpret", **data})
        assert direct.value.code == 403
        prepared = call("/api/prepare-run", data)
        assert not calls
        assert call("/api/confirm-run", {
            "ticket": prepared["ticket"], "confirmed": True, **data,
        }) == {"run_id": "a" * 32}
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **data,
            })
        assert replay.value.code == 403
    assert calls == [{"process": "interpret", **data}]
    assert_empty(tmp_path)


@pytest.mark.parametrize("change", (
    {"text": "INTERPRETAR DOCUMENTO"},
    {"filename": "outra-fonte.txt"},
    {"attachment": base64.b64encode(b"fonte alterada").decode("ascii")},
))
def test_editing_even_an_equivalent_command_revokes_the_ticket(tmp_path, change):
    host = Host(tmp_path)
    data = proposal()
    with http(host) as call:
        prepared = call("/api/prepare-run", data)
        with pytest.raises(HTTPError) as edited:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **{**data, **change},
            })
        assert edited.value.code == 403
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **data,
            })
        assert replay.value.code == 403
        assert call("/api/runs") == []
    assert_empty(tmp_path)


@pytest.mark.parametrize("text", (
    "interpreta documento",
    "não interpretar documento",
    "nunca interpretar documento",
    "sem interpretar documento",
    "interpretar documento agora",
    "interpretar documento.",
    '"interpretar documento"',
    "a frase interpretar documento",
    "interpretar documento e enviar email",
    "interpretar documento; apagar original",
    "apagar original e interpretar documento",
    "interpretar documento\nrever texto",
    "interpretar documento e pesquisar fontes na web",
    "@ interpretar documento",
    "?? interpretar documento",
    "% interpretar documento",
    "@@ interpretar documento",
    "& não interpretar documento",
    "& interpretar documento e apagar ficheiros",
    "interpretar documen\x00to",
    "interpretar documento\x7f",
    "interpretar documento\u200b",
    "＆ interpretar documento",
))
def test_only_the_complete_registered_natural_request_can_get_a_ticket(tmp_path, text):
    host = Host(tmp_path)
    with http(host) as call:
        with pytest.raises(HTTPError) as refused:
            call("/api/prepare-run", proposal(text))
        assert refused.value.code == 403
        assert call("/api/runs") == []
    assert_empty(tmp_path)


@pytest.mark.parametrize("change", (
    {"filename": ""},
    {"attachment": ""},
    {"attachment": "not-base64"},
    {"attachment": "YQ==\n"},
    {"filename": "../fonte.txt"},
    {"filename": "fonte\n.txt"},
    {"process": "interpret"},
    {"approval": True},
    {"capabilities": ["interpret"]},
))
def test_invalid_attachments_and_untrusted_authority_fields_are_refused(tmp_path, change):
    host = Host(tmp_path)
    with http(host) as call:
        with pytest.raises(HTTPError) as refused:
            call("/api/prepare-run", {**proposal(), **change})
        assert refused.value.code == 403
        assert call("/api/runs") == []
    assert_empty(tmp_path)


@pytest.mark.skipif(os.name != "nt", reason="Real Host/LPAC/Job execution requires Windows")
def test_natural_verify_then_interpret_require_independent_gates_and_survive_restart(tmp_path, monkeypatch):
    root = tmp_path / "nexus-data"
    root.mkdir()
    write_config(root)
    host = Host(root)
    original = SOURCE.encode("utf-8")
    completed = []

    with fake_open_notebook() as backend, http(host) as call:
        for process, data in (
            ("verify", proposal("verificar integridade de ficheiro")),
            ("interpret", proposal()),
        ):
            calls_before = backend.calls
            cancelled = call("/api/prepare-run", data)
            assert cancelled["process"] == process
            assert backend.calls == calls_before
            assert call("/api/confirm-run", {
                "ticket": cancelled["ticket"], "confirmed": False, **data,
            }) == {"status": "CANCELLED"}
            assert len(call("/api/runs")) == len(completed)
            assert backend.calls == calls_before

            prepared = call("/api/prepare-run", data)
            run_id = call("/api/confirm-run", {
                "ticket": prepared["ticket"], "confirmed": True, **data,
            })["run_id"]
            state = await_result(call, run_id)
            assert state["status"] == "HUMAN_REQUIRED", state
            assert state["result"]["ai_calls"] == (1 if process == "interpret" else 0)
            assert state["result"]["status"] == ("UNKNOWN" if process == "interpret" else "PASS")
            assert not (root / "canonical" / run_id).exists()
            assert (root / "runs" / run_id / "input.bin").read_bytes() == original
            assert json.loads((root / "runs" / run_id / "request.json").read_bytes()) == {
                "process": process, **data,
            }
            content = state["content"].encode("utf-8")
            assert (root / "creative" / run_id / "content.md").read_bytes() == content
            provenance = json.loads(
                (root / "creative" / run_id / "provenance.json").read_bytes()
            )
            original_sha = hashlib.sha256(original).hexdigest()
            assert state["process_id"] == process
            assert state["input_sha256"] == original_sha
            assert provenance["process_id"] == process
            assert provenance["input_references"] == [{
                "path": "runs/" + run_id + "/input.bin", "sha256": original_sha,
            }]
            assert provenance["output_references"] == [{
                "path": "creative/" + run_id + "/content.md",
                "sha256": hashlib.sha256(content).hexdigest(),
            }]
            assert provenance["execution"]["process_sha256"] == state["process_sha256"]
            assert provenance["execution"]["summary"]["agents_executed"] == [
                "interpret_file" if process == "interpret" else "verify_file",
            ]
            assert provenance["tools"] == [
                item["capability"] for item in state["result"]["evidence"]
            ]
            if process == "verify":
                assert all(
                    item["value"] == original_sha for item in state["result"]["evidence"]
                )

            if process == "interpret":
                assert backend.calls == 1
                assert backend.last_request == {
                    "model_id": CONFIG["model_id"],
                    "transformation_id": CONFIG["transformation_id"],
                    "input_text": SOURCE,
                }
                assert state["result"]["outcome"] == "candidate"
                assert SOURCE in state["content"]
            else:
                assert backend.calls == 0

            with pytest.raises(HTTPError) as replay:
                call("/api/confirm-run", {
                    "ticket": prepared["ticket"], "confirmed": True, **data,
                })
            assert replay.value.code == 403
            assert backend.calls == (1 if process == "interpret" else 0)

            review = call("/api/prepare", {"run_id": run_id})
            with pytest.raises(HTTPError) as denied_review:
                call("/api/approve", {
                    "run_id": run_id, "ticket": review["ticket"], "confirmed": False,
                })
            assert denied_review.value.code == 403
            assert not (root / "canonical" / run_id).exists()
            with pytest.raises(HTTPError) as reused_review:
                call("/api/approve", {
                    "run_id": run_id, "ticket": review["ticket"], "confirmed": True,
                })
            assert reused_review.value.code == 403

            review = call("/api/prepare", {"run_id": run_id})
            assert call("/api/approve", {
                "run_id": run_id, "ticket": review["ticket"], "confirmed": True,
            })["status"] == "PASS"
            assert backend.calls == (1 if process == "interpret" else 0)
            completed.append((run_id, content))
        assert len(completed) == 2
        assert backend.calls == 1

    def no_repeat(*_args, **_kwargs):
        pytest.fail("Recovery must not prepare or execute a capability again")

    monkeypatch.setattr("nexus.adapters.runner.prepare_task", no_repeat)
    monkeypatch.setattr("nexus.host.launch_confined", no_repeat)
    restored = Host(root)
    with http(restored) as call:
        for run_id, content in completed:
            state = call("/api/runs/" + run_id)
            assert state["status"] == "PASS"
            restored.store.check_commit(restored.store.state(run_id))
            assert (root / "canonical" / run_id / "content.md").read_bytes() == content
            assert (root / "canonical" / run_id / "approval.json").is_file()
            assert (root / "canonical" / run_id / "provenance.json").is_file()
            assert (root / "runs" / run_id / "input.bin").read_bytes() == original
    assert backend.calls == 1


@pytest.mark.parametrize("mode", ("wrong-quote", "malformed-output"))
@pytest.mark.skipif(os.name != "nt", reason="Real Host/LPAC/Job execution requires Windows")
def test_natural_interpretation_rejects_bad_peer_output_without_promotion(tmp_path, monkeypatch, mode):
    root = tmp_path / "nexus-data"
    root.mkdir()
    write_config(root)
    host = Host(root)
    data = proposal()
    with fake_open_notebook(mode) as backend, http(host) as call:
        prepared = call("/api/prepare-run", data)
        assert backend.calls == 0
        run_id = call("/api/confirm-run", {
            "ticket": prepared["ticket"], "confirmed": True, **data,
        })["run_id"]
        state = await_result(call, run_id)
        assert state["status"] == "BLOCKED", state
        assert backend.calls == 1
        assert not (root / "creative" / run_id).exists()
        assert not (root / "canonical" / run_id).exists()
        assert (root / "runs" / run_id / "input.bin").read_bytes() == SOURCE.encode("utf-8")
        with pytest.raises(HTTPError) as review:
            call("/api/prepare", {"run_id": run_id})
        assert review.value.code == 403

    def no_repeat(*_args, **_kwargs):
        pytest.fail("Recovery must preserve the refusal, not call the peer again")

    monkeypatch.setattr("nexus.adapters.runner.prepare_task", no_repeat)
    monkeypatch.setattr("nexus.host.launch_confined", no_repeat)
    restored = Host(root)
    with http(restored) as call:
        assert call("/api/runs/" + run_id)["status"] == "BLOCKED"
    assert backend.calls == 1
