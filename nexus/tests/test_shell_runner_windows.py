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
    result = subprocess.run(
        [_shell(), "/D", "/Q", "/C", str(ROOT / "windows/runner-shell.cmd"), process],
        cwd=tmp_path, env=process_environment(tmp_path),
        capture_output=True, timeout=25,
    )
    assert result.returncode == 2, result.stderr.decode("utf-8", "replace")[-1200:]
    assert result.stdout == b""


def test_host_shell_dispatch_cannot_override_lpac_or_execute_invalid_output(tmp_path, monkeypatch):
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
    assert Path(observed["command"][0]).name.lower().startswith("python")
    assert observed["command"][1:4] == [
        "-I", str(ROOT / "adapters/runner.py"), "verify",
    ]
    assert observed["command"][-1] == str(Path(observed["kwargs"]["cwd"]) / "input.bin")
    assert observed["kwargs"]["deny_roots"] == (host.store.root,)
    assert host.store.state(run)["status"] == "BLOCKED"
    assert not list((host.store.root / "canonical").iterdir())


def test_host_shell_dispatch_rejection_never_launches_a_tool(tmp_path, monkeypatch):
    from nexus.contracts import Blocked
    from nexus.host import verify_integrity
    verify_integrity()
    class Refused:
        returncode = 2
        stdout = b""
        stderr = b""
    monkeypatch.setattr("nexus.host.subprocess.run", lambda *_a, **_kw: Refused())
    monkeypatch.setattr("nexus.host.launch_confined",
                        lambda *_a, **_kw: pytest.fail("A Shell recusada lançou a ferramenta"))
    host = Host(tmp_path / "data")
    run = host.store.create(request())
    host.busy.acquire()
    host._run(run)
    assert host.store.state(run)["status"] == "BLOCKED"


def test_real_shell_dispatch_then_native_lpac_result(tmp_path):
    """Actual Windows shell selects; actual isolated Python produces the result."""
    import json
    from nexus.adapters.runner import prepare_task
    from nexus.windows_sandbox import launch_confined
    from nexus.contracts import validate

    source = tmp_path / "source.txt"
    source.write_bytes(b"Nexus Windows shell native acceptance\n")
    work = tmp_path / ".nexus-task-shelltest" / "runs" / ("a" * 32)
    work.mkdir(parents=True)
    roots = prepare_task("verify", source, work, config_root=tmp_path)
    dispatch = subprocess.run(
        [_shell(), "/D", "/Q", "/C", str(ROOT / "windows/runner-shell.cmd"), "verify"],
        cwd=work, env=process_environment(work), capture_output=True, timeout=15,
    )
    assert dispatch.returncode == 0, dispatch.stderr.decode("utf-8", "replace")
    assert dispatch.stdout.strip() == b"NEXUS_SHELL_READY:verify"
    command = [sys.executable, "-I", str(ROOT / "adapters/runner.py"),
               "verify", str(work / "input.bin")]
    with launch_confined(command, cwd=work, env=process_environment(work),
                         read_roots=roots) as proc:
        stdout, stderr = proc.communicate(timeout=35)
        code = proc.returncode
    assert code == 0, {
        "returncode": code, "stdout": stdout[-1500:].decode("utf-8", "replace"),
        "stderr": stderr[-4500:].decode("utf-8", "replace"),
    }
    envelope = json.loads(stdout)
    assert validate("result", envelope["result"])["status"] == "PASS"
    assert envelope["trace"]["process"] == "verify"



@pytest.mark.parametrize("process", ("convert_pdf", "book"))
def test_writer_must_pass_shell_before_sandy_without_bypass(tmp_path, monkeypatch, process):
    """Reproduce the legacy writer exception: refusal by Shell must stop Sandy."""
    from nexus.contracts import Blocked

    calls = []
    class RefusedShell:
        returncode = 2
        stdout = b""
        stderr = b""

    def refuse_shell(*args, **kwargs):
        calls.append(("shell", args))
        return RefusedShell()

    def reject_writer(*args, **kwargs):
        calls.append(("writer", args))
        raise Blocked("Writer must not run after a refused Shell dispatch")

    def reject_preparation(*args, **kwargs):
        calls.append(("preparation", args))
        raise Blocked("No preparation or external call before Shell authorization")

    monkeypatch.setattr("nexus.adapters.runner.prepare_task", reject_preparation)
    monkeypatch.setattr("nexus.host.subprocess.run", refuse_shell)
    monkeypatch.setattr("nexus.adapters.writer_sandy.convert", reject_writer)
    host = Host(tmp_path / "data")
    item = request()
    item["process"] = process
    run = host.store.create(item)
    host.busy.acquire()
    host._run(run)
    assert [name for name, _ in calls] == ["shell"], calls
    assert host.store.state(run)["status"] == "BLOCKED"
    assert not list((host.store.root / "canonical").iterdir())


def test_shell_registry_is_exactly_the_host_authorized_process_set():
    """No secondary dispatch registry can drift away from the Shell."""
    import re
    from nexus.capability_router import BUILTIN_CAPABILITIES
    from nexus.adapters.runner import PROCESS_TO_TOOL
    from nexus.contracts import load_policy

    script = (ROOT / "windows" / "runner-shell.cmd").read_text("utf-8")
    actual = re.findall(r'(?im)^if /i "%~1"=="([a-z_]+)" goto dispatch$', script)
    expected = set(load_policy()["processes"])
    assert len(actual) == len(set(actual))
    assert set(actual) == expected
    assert expected == set(PROCESS_TO_TOOL)
    assert expected == {item.process for item in BUILTIN_CAPABILITIES}
    assert script.count(":dispatch") == 1



@pytest.mark.parametrize("process", (
    "verify", "interpret", "proofread", "convert_pdf", "video",
    "podcast", "visual_podcast", "book", "music", "web",
))
def test_every_process_shell_refusal_prevents_all_preparation(tmp_path, monkeypatch, process):
    """Prevent tools, networking and Writer even before Host preparation."""
    from nexus.contracts import Blocked

    events = []
    class Refused:
        returncode = 2
        stdout = b""
        stderr = b""

    def shell_refuse(*_args, **_kwargs):
        events.append("shell")
        return Refused()

    def preparation_forbidden(*_args, **_kwargs):
        events.append("preparation")
        raise Blocked("Preparation bypassed Shell")

    monkeypatch.setattr("nexus.host.subprocess.run", shell_refuse)
    monkeypatch.setattr("nexus.adapters.runner.prepare_task", preparation_forbidden)
    host = Host(tmp_path / process)
    req = request()
    req["process"] = process
    run = host.store.create(req)
    host.busy.acquire()
    host._run(run)
    assert events == ["shell"], (process, events)
    assert host.store.state(run)["status"] == "BLOCKED"
    assert not list((host.store.root / "creative").iterdir())
    assert not list((host.store.root / "canonical").iterdir())
