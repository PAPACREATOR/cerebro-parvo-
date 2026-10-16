"""IMP-001 additive acceptance checks for the current Folha/Store boundary.

Preserves the sealed Host/Kernel/Store implementation. Only disposable fixtures.
These tests do not claim stream uploads, physical power-loss recovery or full IMP closure.
"""
import base64
import hashlib
from urllib.error import HTTPError

import pytest

from nexus.capability_router import BUILTIN_CAPABILITIES
from nexus.contracts import Blocked
from nexus.host import Host
from nexus.store import Store
from nexus.tests.test_reverse_flow import http


def _input(raw):
    return {
        "process": "verify",
        "text": "Verificar a integridade do ficheiro.",
        "filename": "Relatório_ação_日本語_2026.bin",
        "attachment": base64.b64encode(raw).decode("ascii"),
    }


def _folha_input(raw):
    request = _input(raw)
    command = next(item.command for item in BUILTIN_CAPABILITIES if item.process == "verify")
    request["text"] = "& " + command
    request.pop("process")
    return request


@pytest.mark.parametrize("raw", [
    b"\x00\xff\x80\noriginal\x00",
    "Ação — 日本語 — linha 2\n".encode("utf-8"),
    bytes(range(256)) * 32,
])
def test_folha_prepares_exact_binary_unicode_without_writing_or_executing(tmp_path, raw):
    host = Host(tmp_path)
    request = _folha_input(raw)
    with http(host) as call:
        prepared = call("/api/prepare-run", request)
        assert prepared["process"] == "verify"
        assert prepared["attachment_bytes"] == len(raw)
        assert prepared["attachment_sha256"] == hashlib.sha256(raw).hexdigest()
        assert call("/api/runs") == []
        assert call("/api/confirm-run", {
            **request, "ticket": prepared["ticket"], "confirmed": False,
        }) == {"status": "CANCELLED"}
        assert call("/api/runs") == []
    assert all(not any((tmp_path / area).iterdir())
               for area in ("runs", "creative", "canonical"))


def test_store_preserves_exact_attachment_bytes_on_restart_and_distinct_receipts(tmp_path):
    raw = bytes(range(256)) * 127 + b"\x00\xff\x00"
    store = Store(tmp_path)
    first = store.create(_input(raw))
    second = store.create(_input(raw))
    assert first != second
    assert (store.path("runs", first) / "input.bin").read_bytes() == raw
    assert (store.path("runs", second) / "input.bin").read_bytes() == raw
    recovered = Store(tmp_path)
    for run_id in (first, second):
        state = recovered.state(run_id)
        assert state["input_sha256"] == hashlib.sha256(raw).hexdigest()
        assert state["title"] == "Relatório_ação_日本語_2026.bin"
        assert (recovered.path("runs", run_id) / "input.bin").read_bytes() == raw
        recovered.check_input(state)
        assert not recovered.path("creative", run_id).exists()
        assert not recovered.path("canonical", run_id).exists()


@pytest.mark.parametrize("attachment", [
    "*invalid-base64*",
    base64.b64encode(b"x" * (2097152 + 1)).decode("ascii"),
], ids=("invalid-base64", "oversized-one-byte"))
def test_invalid_or_oversized_attachment_never_creates_run(tmp_path, attachment):
    store = Store(tmp_path)
    request = _input(b"valid")
    request["attachment"] = attachment
    with pytest.raises(Blocked):
        store.create(request)
    assert not any((tmp_path / area).iterdir()
                   for area in ("runs", "creative", "canonical"))


def test_folha_refuses_empty_upload_without_side_effects(tmp_path):
    host = Host(tmp_path)
    request = _folha_input(b"")
    with http(host) as call:
        with pytest.raises(HTTPError) as error:
            call("/api/prepare-run", request)
        assert error.value.code == 403
        assert call("/api/runs") == []
    assert all(not any((tmp_path / area).iterdir())
               for area in ("runs", "creative", "canonical"))
