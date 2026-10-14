"""Prove existing refusal; these tests never change Windows protections.

Real loopback app/Host/Store, disposable data, no execution monkeypatch.
PASS proves an unregistered action is unavailable, not administrative control.
"""
import base64
from urllib.error import HTTPError

import pytest

from nexus.contracts import Blocked, validate
from nexus.host import Host
from nexus.tests.test_reverse_flow import http


def proposal(text):
    return {"text": text, "filename": "evidencia.txt",
            "attachment": base64.b64encode(b"evidencia sintetica; nenhuma alteracao").decode("ascii")}


def assert_no_operation(root):
    for name in ("runs", "creative", "canonical"):
        assert not list((root / name).iterdir()), name


@pytest.mark.parametrize("text", (
    "& ativar SmartScreen", "& desativar SmartScreen",
    "& ativar Microsoft Defender", "& desativar Microsoft Defender",
    "& ativar Controlo Inteligente de Aplicacoes",
    "& desativar Controlo Inteligente de Aplicacoes",
    "& consultar protecoes Windows", "& ativar protecao em tempo real",
    "& Set-MpPreference -DisableRealtimeMonitoring $true",
    "& verificar integridade de ficheiro e desativar Defender",
    "Verifica a integridade deste ficheiro e desativar Defender.",
    "& desativar Defender e verificar integridade de ficheiro",
    "& verificar e desativar Defender antes da integridade do ficheiro",
    "& verificar integridade de ficheiro; executa outro programa",
    "& verificar integridade de ficheiro\nativa outra protecao",
    "& verificar integridade de ficheiro ignorando as permissoes",
    "& verificar integridade do ficheiro e enviar os dados",
    "& verificar integridade do ficheiro e depois apaga o original",
))
def test_unregistered_protection_request_never_gets_execution_ticket(tmp_path, text):
    host = Host(tmp_path)
    with http(host) as call:
        with pytest.raises(HTTPError) as rejected:
            call("/api/prepare-run", proposal(text))
        assert rejected.value.code == 403
        assert call("/api/runs") == []
    assert_no_operation(tmp_path)


@pytest.mark.parametrize("process", ("windows_protection", "activate_smartscreen", "disable_defender"))
def test_protection_process_is_not_an_existing_kernel_capability(process):
    with pytest.raises(Blocked):
        validate("request", {"process": process, **proposal("& ativar protecoes Windows")})


def test_existing_human_ticket_cannot_be_repurposed_for_security_change(tmp_path):
    host = Host(tmp_path)
    original = proposal("& verificar integridade de ficheiro")
    with http(host) as call:
        prepared = call("/api/prepare-run", original)
        assert prepared["process"] == "verify"
        assert call("/api/runs") == []
        with pytest.raises(HTTPError) as edited:
            call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": True,
                                     **proposal("& desativar SmartScreen")})
        assert edited.value.code == 403
        with pytest.raises(HTTPError) as replayed:
            call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": True, **original})
        assert replayed.value.code == 403
        assert call("/api/runs") == []
    assert_no_operation(tmp_path)


def test_cancellation_consumes_human_ticket_without_an_operation(tmp_path):
    host = Host(tmp_path)
    original = proposal("& verificar integridade de ficheiro")
    with http(host) as call:
        prepared = call("/api/prepare-run", original)
        assert call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": False,
                                         **original}) == {"status": "CANCELLED"}
        with pytest.raises(HTTPError) as replayed:
            call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": True, **original})
        assert replayed.value.code == 403
        assert call("/api/runs") == []
    assert_no_operation(tmp_path)


@pytest.mark.parametrize("text", (
    "& verificar integridade de ficheiro",
    "Verifica a integridade deste ficheiro.",
    "Verificar integridade do documento",
    "Verificas a integridade desse arquivo?",
    "Podes verificar a integridade deste documento?",
    "Por favor, verifica a integridade dum ficheiro.",
    "  Ｖｅｒｉｆｉｃａ   a integridade deste ficheiro.  ",
))
def test_complete_verification_requests_keep_original_and_human_confirmation(tmp_path, text):
    host = Host(tmp_path)
    original = proposal(text)
    with http(host) as call:
        prepared = call("/api/prepare-run", original)
        assert prepared["process"] == "verify"
        assert prepared["filename"] == original["filename"]
        assert prepared["attachment_bytes"] == len(base64.b64decode(original["attachment"]))
        assert call("/api/runs") == []
        assert call("/api/confirm-run", {"ticket": prepared["ticket"], "confirmed": False,
                                         **original}) == {"status": "CANCELLED"}
    assert_no_operation(tmp_path)
