"""Kernel-owned crash/restart contracts. Synthetic data only."""
import json

from nexus.store import Store
from nexus.tests.test_store import request, result


def test_restart_with_durable_executor_result_requires_reconciliation_not_generic_fail(tmp_path):
    """FAIL-first: external result exists, but Kernel crashed before Store.accept.

    The executor is disposable. On restart, the Kernel must not erase the distinction
    between "nothing completed" and "a durable result exists but is not committed".
    The safe state is explicit reconciliation; Canonical must remain untouched.
    """
    store = Store(tmp_path)
    run_id = store.create(request())
    run = store.path("runs", run_id)

    envelope = {
        "result": result(),
        "trace": {
            "engine": "microsoft/conductor",
            "version": "synthetic",
            "summary": {"status": "completed"},
            "events": [],
            "workflow_sha256": "0" * 64,
        },
    }
    (run / "execution.stdout.json").write_text(
        json.dumps(envelope, ensure_ascii=False), encoding="utf-8"
    )
    (run / "execution.stderr.txt").write_bytes(b"")

    restarted = Store(tmp_path)
    state = restarted.state(run_id)

    assert state["status"] == "BLOCKED"
    assert state["commit_status"] == "RECOVERY_REQUIRED"
    assert (run / "execution.stdout.json").is_file()
    assert not list((tmp_path / "canonical").iterdir())
