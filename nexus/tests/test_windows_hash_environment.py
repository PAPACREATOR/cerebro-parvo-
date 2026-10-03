"""Native hash probes under Host's reduced environment and hidden console."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from nexus.contracts import ROOT
from nexus.host import process_environment

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Requires native Windows PowerShell")


def execute_hash(process, source, work):
    workflow = YAML(typ="safe").load((ROOT / "processes" / (process + ".yaml")).read_text("utf-8"))
    step = next(item for item in workflow["agents"] if item["name"] == "hash_windows")
    powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    result = subprocess.run(
        [str(powershell), *step["args"]], input=str(source).encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work,
        env=process_environment(work), creationflags=subprocess.CREATE_NO_WINDOW,
        timeout=step["timeout"],
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    return json.loads(result.stdout.decode("utf-8")), result.stderr


@pytest.mark.parametrize("process", ["check", "verify"])
@pytest.mark.parametrize("filename,raw", [
    ("simple.txt", b"Nexus synthetic text\n"),
    ("ação ' & $ com espaços.bin", bytes(range(256))),
    ("empty.bin", b""),
])
def test_hash_runs_without_user_environment(tmp_path, process, filename, raw):
    source = tmp_path / filename
    source.write_bytes(raw)
    payload, _ = execute_hash(process, source, tmp_path)
    assert payload == {"status": "PASS", "sha256": hashlib.sha256(raw).hexdigest(),
                       "capability": "windows.dotnet-sha256"}
    assert source.read_bytes() == raw


@pytest.mark.parametrize("process", ["check", "verify"])
def test_missing_file_returns_json_failure_and_diagnostic(tmp_path, process):
    payload, stderr = execute_hash(process, tmp_path / "missing.bin", tmp_path)
    assert payload["status"] == "FAIL"
    assert payload["sha256"] is None
    assert stderr
