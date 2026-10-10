"""FAIL-first isolated Host/OpenNotebook startup fault injection.

No production changes, real provider calls, PC installation, or Canonical writes.
Expected invariant: a failed worker launch must not leave a permanently busy
Host or a request incorrectly marked as executing.
"""
import threading

import pytest

from nexus.host import Host
from nexus.tests.test_store import request


def test_notebook_worker_start_failure_is_recoverable_without_provider_call(tmp_path, monkeypatch):
    host = Host(tmp_path)
    provider_calls = []

    def never_run(_run_id):
        provider_calls.append("unexpected")

    def fail_start(_thread):
        raise RuntimeError("synthetic thread-start failure")

    monkeypatch.setattr(host, "_run", never_run)
    monkeypatch.setattr(threading.Thread, "start", fail_start)

    with pytest.raises(RuntimeError, match="synthetic thread-start failure"):
        host.start({**request(), "process": "interpret"}, host.session)

    assert provider_calls == []
    assert not host.busy.locked(), "A failed worker start must release the Host busy lock"
    assert not list((tmp_path / "creative").iterdir())
    assert not list((tmp_path / "canonical").iterdir())

    states = [host.store.state(p.name) for p in (tmp_path / "runs").iterdir() if p.is_dir()]
    assert len(states) == 1
    assert states[0]["status"] != "RUNNING", (
        "A request whose worker never started must not remain RUNNING"
    )
