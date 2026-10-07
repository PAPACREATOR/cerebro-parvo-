import os
import subprocess
import sys
from pathlib import Path

from nexus.store import Store


def test_restart_surfaces_create_crash_after_input_is_durable(tmp_path):
    script = r"""
import os
import sys
from pathlib import Path
import nexus.store as store_module

root = Path(sys.argv[1])
real_atomic = store_module.atomic
calls = {"count": 0}

def crash_after_first_durable_write(path, data):
    real_atomic(path, data)
    calls["count"] += 1
    if calls["count"] == 1:
        os._exit(91)

store_module.atomic = crash_after_first_durable_write
request = {
    "process": "verify",
    "text": "bytes preservados após crash",
    "filename": "",
    "attachment": "",
}
store_module.Store(root).create(request)
"""
    crashed = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        cwd=str(Path(__file__).parents[2]),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert crashed.returncode == 91, crashed.stdout + crashed.stderr

    runs = [path for path in (tmp_path / "runs").iterdir() if path.is_dir()]
    assert len(runs) == 1
    run = runs[0]
    original = run / "input.bin"
    assert original.read_bytes() == b"bytes preservados apÃ³s crash"
    assert not (run / "state.json").exists()

    restarted = Store(tmp_path)
    recovered = restarted.state(run.name)

    assert recovered["status"] == "BLOCKED"
    assert recovered["commit_status"] == "RECOVERY_REQUIRED"
    assert recovered["run_id"] == run.name
    assert recovered["input_sha256"]
    assert original.read_bytes() == b"bytes preservados apÃ³s crash"
    assert not (tmp_path / "canonical" / run.name).exists()
