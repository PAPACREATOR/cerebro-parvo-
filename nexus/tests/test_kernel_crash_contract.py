"""Independent review of Kernel-owned crash/restart reconciliation.

Synthetic data only. This file does not implement recovery; it verifies the
already-implemented T01 contract from the Work branch.
"""
import json

from nexus.store import Store
from nexus.tests.test_store import request, result


def test_restart_reconciles_durable_executor_result_without_generic_fail(tmp_path):
    """Executor output is durable; Kernel crashed before Store.accept.

    Restart must reconcile the saved result without creating Canonical or
    degrading the operation to a generic FAIL.
    """
    store = Store(tmp_path)
    run_id = store.create(request())
    run = store.path("runs", run_id)

    envelope = {
        "result": result(),
        "trace": {
            "engine": "synthetic-disposable-executor",
            "version": "synthetic",
            "summary": {"status": "completed"},
            "events": [],
        },
    }
    raw = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
    (run / "execution.stdout.json").write_bytes(raw)
    (run / "execution.stderr.txt").write_bytes(b"")

    restarted = Store(tmp_path)
    state = restarted.state(run_id)

    assert state["status"] == "HUMAN_REQUIRED"
    assert state["status"] != "FAIL"
    assert (run / "execution.stdout.json").read_bytes() == raw
    assert restarted.check_candidate(state)["execution"]["engine"] == "synthetic-disposable-executor"
    assert not restarted.path("canonical", run_id).exists()
