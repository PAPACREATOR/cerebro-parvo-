"""Natural registered commands retain the original product human gates."""
import base64
import hashlib
import json
import os
import time
from urllib.error import HTTPError

import pytest

from nexus.host import Host
from nexus.tests.test_reverse_flow import http


NATURAL_REQUESTS = (
    ("rever texto", "proofread"),
    ("  Rever\t  texto\n", "proofread"),
    ("Ｒｅｖｅｒ ｔｅｘｔｏ", "proofread"),
    ("preparar plano de pesquisa web", "web"),
    ("  Preparar\t plano de pesquisa  web\n", "web"),
    ("Ｐｒｅｐａｒａｒ ｐｌａｎｏ ｄｅ ｐｅｓｑｕｉｓａ ｗｅｂ", "web"),
)


def proposal(text):
    raw = "Consulta: fontes sobre turismo no Alentejo\n".encode("utf-8")
    return {"text": text, "filename": "fonte.txt",
            "attachment": base64.b64encode(raw).decode("ascii")}


def assert_no_operation(root):
    for name in ("runs", "creative", "canonical"):
        assert not list((root / name).iterdir()), name


@pytest.mark.parametrize(("text", "process"), NATURAL_REQUESTS)
def test_complete_natural_registered_requests_keep_original_and_require_confirmation(tmp_path, text, process):
    host = Host(tmp_path)
    data = proposal(text)
    with http(host) as call:
        prepared = call("/api/prepare-run", data)
        assert prepared["process"] == process
        assert prepared["attachment_sha256"] == hashlib.sha256(base64.b64decode(data["attachment"])).hexdigest()
        assert call("/api/runs") == []
        assert call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": False,
                                         **data}) == {"status": "CANCELLED"}
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": True, **data})
        assert replay.value.code == 403
    assert_no_operation(tmp_path)


@pytest.mark.parametrize(("text", "process"), (NATURAL_REQUESTS[0], NATURAL_REQUESTS[3]))
def test_natural_allow_dispatches_only_the_exact_confirmed_request(tmp_path, monkeypatch, text, process):
    host = Host(tmp_path)
    calls = []

    def capture(request, session):
        host.authorize(session)
        calls.append(request)
        return {"run_id": "a" * 32}

    monkeypatch.setattr(host, "start", capture)
    data = proposal(text)
    with http(host) as call:
        with pytest.raises(HTTPError) as direct:
            call("/api/run", {"process": process, **data})
        assert direct.value.code == 403
        prepared = call("/api/prepare-run", data)
        assert not calls
        assert call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": True,
                                         **data}) == {"run_id": "a" * 32}
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": True, **data})
        assert replay.value.code == 403
    assert calls == [{"process": process, **data}]
    assert_no_operation(tmp_path)


@pytest.mark.parametrize("text", (NATURAL_REQUESTS[0][0], NATURAL_REQUESTS[3][0]))
@pytest.mark.parametrize("field", ("text", "attachment"))
def test_editing_a_natural_request_consumes_ticket_without_dispatch(tmp_path, text, field):
    host = Host(tmp_path)
    data = proposal(text)
    edited = dict(data, text=text + " e envia os dados") if field == "text" else dict(
        data, attachment=base64.b64encode(b"alterado").decode("ascii"))
    with http(host) as call:
        prepared = call("/api/prepare-run", data)
        with pytest.raises(HTTPError) as changed:
            call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": True, **edited})
        assert changed.value.code == 403
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": True, **data})
        assert replay.value.code == 403
        assert call("/api/runs") == []
    assert_no_operation(tmp_path)


@pytest.mark.parametrize("text", (
    "rever texto e apaga o original",
    "apaga o original e rever texto",
    "rever e enviar dados antes do texto",
    "rever texto; executa outro programa",
    "rever texto\nenvia os dados",
    "não rever texto",
    "rever texto agora",
    "preparar plano de pesquisa web e enviar email",
    "enviar email e preparar plano de pesquisa web",
    "preparar plano de pesquisa e enviar dados antes da web",
    "preparar plano de pesquisa web; executa outro programa",
    "preparar plano de pesquisa web\napaga o original",
    "não preparar plano de pesquisa web",
    "preparar plano de pesquisa web agora",
    "pesquisar na web",
    "melhora este texto",
    "@ rever texto",
    "% rever texto",
    "# rever texto",
    "& preparar plano de pesquisa web",
    "＆ rever texto",
))
def test_unknown_compound_negative_and_wrong_intent_requests_stay_blocked(tmp_path, text):
    host = Host(tmp_path)
    with http(host) as call:
        with pytest.raises(HTTPError) as refused:
            call("/api/prepare-run", proposal(text))
        assert refused.value.code == 403
        assert call("/api/runs") == []
    assert_no_operation(tmp_path)


@pytest.mark.parametrize("text", (NATURAL_REQUESTS[0][0], NATURAL_REQUESTS[3][0]))
def test_natural_requests_still_require_an_attachment(tmp_path, text):
    host = Host(tmp_path)
    with http(host) as call:
        with pytest.raises(HTTPError) as refused:
            call("/api/prepare-run", {"text": text, "filename": "", "attachment": ""})
        assert refused.value.code == 403
    assert_no_operation(tmp_path)


@pytest.mark.skipif(os.name != "nt", reason="Real Windows Host/LPAC/Job not available")
def test_natural_web_spec_runs_through_native_host_and_both_human_gates(tmp_path, monkeypatch):
    host = Host(tmp_path)
    data = proposal("preparar plano de pesquisa web")
    original = base64.b64decode(data["attachment"])
    with http(host) as call:
        denied = call("/api/prepare-run", data)
        assert call("/api/confirm-run", {"ticket": denied["ticket"], "confirmed": False,
                                         **data}) == {"status": "CANCELLED"}
        assert_no_operation(tmp_path)
        prepared = call("/api/prepare-run", data)
        assert prepared["process"] == "web"
        run = call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": True,
                                       **data})["run_id"]
        deadline = time.monotonic() + 30
        state = call("/api/runs/" + run)
        while state["status"] == "RUNNING" and time.monotonic() < deadline:
            time.sleep(0.1)
            state = call("/api/runs/" + run)
        assert state["status"] == "HUMAN_REQUIRED", state
        assert not (tmp_path / "canonical" / run).exists()
        result = json.loads((tmp_path / "creative" / run / "result.json").read_bytes())
        assert result["status"] == "UNKNOWN"
        assert result["ai_calls"] == 0
        assert result["evidence"][0]["capability"] == "web/query-spec"
        assert (tmp_path / "runs" / run / "input.bin").read_bytes() == original
        assert json.loads((tmp_path / "runs" / run / "request.json").read_bytes()) == {"process": "web", **data}
        assert not (tmp_path / "creative" / run / "resultado.pdf").exists()
        approval = call("/api/prepare", {"run_id": run})
        assert call("/api/approve", {"run_id": run, "ticket": approval["ticket"],
                                     "confirmed": True})["status"] == "PASS"

    def no_repeat(*_args, **_kwargs):
        pytest.fail("Restart must not repeat the confirmed native task")

    monkeypatch.setattr("nexus.host.launch_confined", no_repeat)
    restored = Host(tmp_path)
    restored.store.check_commit(restored.store.state(run))
    assert restored.store.state(run)["status"] == "PASS"
    assert (tmp_path / "runs" / run / "input.bin").read_bytes() == original
