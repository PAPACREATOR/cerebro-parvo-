"""Windows PowerShell runner contract: fixed process list and native LPAC launch."""
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
    shell = Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    assert shell.is_file()
    return str(shell)


@pytest.mark.parametrize("process", ["shell", "approve", "canonical", "web;whoami", "verify;echo"])
def test_shell_rejects_unknown_process_without_invoking_python(tmp_path, process):
    source = tmp_path / "input.bin"
    source.write_bytes(b"unchanged")
    result = subprocess.run(
        [_shell(), "-NoLogo", "-NoProfile", "-NonInteractive",
         "-ExecutionPolicy", "Bypass", "-File",
         str(ROOT / "windows/runner-shell.ps1"),
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
    assert Path(observed["command"][0]).name.lower() == "powershell.exe"
    assert observed["command"][7] == str(ROOT / "windows/runner-shell.ps1")
    assert observed["command"][-2] == "verify"
    assert observed["command"][-1] == str(observed["kwargs"]["cwd"] / "input.bin") if isinstance(observed["kwargs"]["cwd"], Path) else str(Path(observed["kwargs"]["cwd"]) / "input.bin")
    assert observed["kwargs"]["deny_roots"] == (host.store.root,)
    assert host.store.state(run)["status"] == "BLOCKED"
    assert not list((host.store.root / "canonical").iterdir())
