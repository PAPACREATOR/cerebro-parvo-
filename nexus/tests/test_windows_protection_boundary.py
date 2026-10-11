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
