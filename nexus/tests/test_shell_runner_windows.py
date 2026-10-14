"""Windows CMD Shell runner: fixed process list and native LPAC launch."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

from nexus.contracts import ROOT
from nexus.host import Host, process_environment
from nexus.tests.test_store import request


pytestmark = pytest.mark.skipif(os.name != "nt", reason="Native Windows only")


def _shell():
    shell = Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32" / "cmd.exe"
    assert shell.is_file()
    return str(shell)


@pytest.mark.parametrize("process", ["shell", "approve", "canonical", "web;whoami", "verify;echo"])
def test_shell_rejects_unknown_process_without_invoking_python(tmp_path, process):
    source = tmp_path / "input.bin"
    source.write_bytes(b"unchanged")
    result = subprocess.run(
        [_shell(), "/D", "/Q", "/C", str(ROOT / "windows/runner-shell.cmd"),
         sys.executable, str(ROOT / "adapters/runner.py"), process, str(source)],
        cwd=tmp_path,
        env=process_environment(tmp_path),
        capture_output=True,
        timeout=25,
    )
    assert result.returncode == 2, result.stderr.decode("utf-8", "replace")[-1200:]
    assert result.stdout == b""
    assert source.read_bytes() == b"unchanged"


def test_host_shell_still_uses_native_lp_ac_and_does_not_accept_invalid_output(tmp_path, monkeypatch):
    observed = {}

    class InvalidReply:
        returncode = 0
        def __enter__(self):
            return self
        def __exit__(self, *_args):
            pass
        def communicate(self, **_kwargs):
            return b"NOT-JSON", b""

    def capture(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        return InvalidReply()

    monkeypatch.setattr("nexus.host.launch_confined", capture)
    host = Host(tmp_path / "data")
    run = host.store.create(request())
    host.busy.acquire()
    host._run(run)
    assert Path(observed["command"][0]).name.lower() == "cmd.exe"
    assert observed["command"][4] == str(ROOT / "windows/runner-shell.cmd")
    assert observed["command"][-2] == "verify"
    assert observed["command"][-1] == str(observed["kwargs"]["cwd"] / "input.bin") if isinstance(observed["kwargs"]["cwd"], Path) else str(Path(observed["kwargs"]["cwd"]) / "input.bin")
    assert observed["kwargs"]["deny_roots"] == (host.store.root,)
    assert host.store.state(run)["status"] == "BLOCKED"
    assert not list((host.store.root / "canonical").iterdir())


def test_real_shell_inside_native_lpac_returns_valid_result(tmp_path):
    """Actual OS boundary: output diagnostic is an error, never a fake PASS."""
    import json
    from nexus.adapters.runner import prepare_task
    from nexus.windows_sandbox import launch_confined
    from nexus.contracts import validate

    source = tmp_path / "source.txt"
    source.write_bytes(b"Nexus Windows shell native acceptance\n")
    work = tmp_path / ".nexus-task-shelltest" / "runs" / ("a" * 32)
    work.mkdir(parents=True)
    roots = prepare_task("verify", source, work, config_root=tmp_path)
    # Diagnostic gates exercise the exact same native LPAC token and job.
    # Distinguish shell startup, reading the fixed script, and child Python
    # execution. None of these probes grants new permissions or fakes PASS.
    probes = (
        ([_shell(), "/D", "/Q", "/C", "echo NEXUS_SHELL_ALIVE"], 0),
        ([_shell(), "/D", "/Q", "/C",
          str(ROOT / "windows/runner-shell.cmd"),
          sys.executable, str(ROOT / "adapters/runner.py"),
          "not_registered", str(work / "input.bin")], 2),
    )
    for probe, expected in probes:
        with launch_confined(probe, cwd=work, env=process_environment(work),
                             read_roots=roots) as diagnostic:
            out, err = diagnostic.communicate(timeout=35)
            exit_code = diagnostic.returncode
        assert exit_code == expected, {
            "phase": "shell-start" if expected == 0 else "shell-script",
            "returncode": exit_code,
            "stdout": out.decode("utf-8", "replace")[-800:],
            "stderr": err.decode("utf-8", "replace")[-2000:],
        }
    command = [
        _shell(), "/D", "/Q", "/C",
        str(ROOT / "windows/runner-shell.cmd"),
        sys.executable, str(ROOT / "adapters/runner.py"),
        "verify", str(work / "input.bin"),
    ]
    with launch_confined(command, cwd=work, env=process_environment(work),
                         read_roots=roots) as proc:
        stdout, stderr = proc.communicate(timeout=35)
        code = proc.returncode
    assert code == 0, {
        "returncode": code,
        "stdout": stdout[-1500:].decode("utf-8", "replace"),
        "stderr": stderr[-4500:].decode("utf-8", "replace"),
    }
    envelope = json.loads(stdout)
    assert validate("result", envelope["result"])["status"] == "PASS"
    assert envelope["trace"]["process"] == "verify"
