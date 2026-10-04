"""Direct deterministic verify capability for equivalence testing.

This module does not own persistence, approval or recovery. It only executes
the existing verify contract without a workflow engine.
"""
import json
import os
import subprocess
from pathlib import Path

from nexus.adapters.tools import hash_python, compare, report
from nexus.contracts import Blocked

POLICY = {
    "agreement": "PASS",
    "conflict": "UNKNOWN",
    "unknown": "UNKNOWN",
    "failure": "FAIL",
}


def powershell_executable():
    root = os.environ.get("SystemRoot") or os.environ.get("WINDIR")
    if not root:
        raise Blocked("PowerShell Windows indisponível.")
    return str(Path(root) / "System32/WindowsPowerShell/v1.0/powershell.exe")


def hash_windows(path, *, executable=None, timeout=15):
    script = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
$p = [Console]::In.ReadToEnd().TrimEnd([char]10, [char]13)
try {
  $algorithm = [System.Security.Cryptography.SHA256]::Create()
  try { $hash = [BitConverter]::ToString($algorithm.ComputeHash([System.IO.File]::ReadAllBytes($p))).Replace('-', '').ToLowerInvariant() }
  finally { $algorithm.Dispose() }
  [Console]::Out.WriteLine('{"status":"PASS","sha256":"' + $hash + '","capability":"windows.dotnet-sha256"}')
} catch {
  [Console]::Error.WriteLine($_.Exception.Message)
  [Console]::Out.WriteLine('{"status":"FAIL","sha256":null,"capability":"windows.dotnet-sha256","error":"Não foi possível ler o ficheiro."}')
}
"""
    command = executable or powershell_executable()
    try:
        completed = subprocess.run(
            [command, "-NoProfile", "-NonInteractive", "-Command", script],
            input=str(Path(path).resolve()),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise Blocked("A verificação Windows excedeu o tempo permitido.") from error
    except OSError as error:
        raise Blocked("PowerShell Windows indisponível.") from error

    if completed.returncode != 0 or not completed.stdout.strip():
        raise Blocked("A verificação Windows falhou.")
    try:
        value = json.loads(completed.stdout.strip().splitlines()[-1])
    except (ValueError, UnicodeError) as error:
        raise Blocked("A verificação Windows devolveu dados inválidos.") from error
    if not isinstance(value, dict) or value.get("status") not in ("PASS", "FAIL"):
        raise Blocked("A verificação Windows devolveu contrato inválido.")
    return value


def execute(path, *, powershell=None, timeout=15):
    a = hash_windows(path, executable=powershell, timeout=timeout)
    b = hash_python(path)
    comparison = compare(a, b)
    result = report({"comparison": comparison, "status": POLICY[comparison["outcome"]]})
    return {
        "result": result,
        "trace": {
            "engine": "nexus/python-direct",
            "version": "1.0.0",
            "summary": {
                "usage": {"total_tokens": 0},
                "agents_executed": ["hash_windows", "hash_python", "compare", "report"],
            },
            "events": [
                {"type": "step.completed", "step": "hash_windows"},
                {"type": "step.completed", "step": "hash_python"},
                {"type": "step.completed", "step": "compare"},
                {"type": "step.completed", "step": "report"},
            ],
        },
    }
