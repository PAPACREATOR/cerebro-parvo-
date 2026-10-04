"""Deterministic Nexus executor.

Historical filename retained during the replacement Lab so Kernel contracts can
be compared without changing the Host boundary. This module has no Microsoft
Conductor dependency and no autonomous provider.
"""
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from nexus.adapters import languagetool, notebook, office
from nexus.adapters.tools import compare, hash_python, report
from nexus.contracts import Blocked, ROOT, strict_json


_ALLOWED = {"verify", "interpret", "proofread", "convert_pdf"}


def _hash_windows(path, powershell):
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
    try:
        completed = subprocess.run(
            [powershell, "-NoProfile", "-NonInteractive", "-Command", script],
            input=str(path),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Blocked("A verificação Windows não ficou disponível.") from error
    if completed.returncode != 0 or not completed.stdout.strip():
        raise Blocked("A verificação Windows falhou.")
    value = strict_json(completed.stdout.strip().splitlines()[-1])
    if not isinstance(value, dict) or value.get("status") not in ("PASS", "FAIL"):
        raise Blocked("A verificação Windows devolveu dados inválidos.")
    return value


def _summary(steps):
    return {
        "status": "completed",
        "usage": {"total_tokens": 0},
        "agents_executed": list(steps),
        "steps_executed": list(steps),
    }


def _trace(steps):
    return {
        "engine": "nexus/python-deterministic",
        "version": "1.0.0",
        "summary": _summary(steps),
        "events": [{"type": "step_completed", "step": step} for step in steps],
    }


async def execute(workflow_path, inputs):
    workflow_path = Path(workflow_path).resolve()
    process = workflow_path.stem
    expected = (ROOT / "processes" / (process + ".yaml")).resolve()
    if process not in _ALLOWED or workflow_path != expected or not expected.is_file():
        raise Blocked("Processo indisponível.")

    input_path = Path(inputs["input_path"]).resolve()
    if process == "verify":
        powershell = inputs.get("powershell")
        if not isinstance(powershell, str) or not powershell:
            raise Blocked("PowerShell indisponível.")
        windows = _hash_windows(input_path, powershell)
        python = hash_python(input_path)
        comparison = compare(windows, python)
        policy = {
            "agreement": "PASS",
            "conflict": "UNKNOWN",
            "unknown": "UNKNOWN",
            "failure": "FAIL",
        }
        result = report({"comparison": comparison, "status": policy[comparison["outcome"]]})
        steps = ("hash_windows", "hash_python", "compare", "report")
    elif process == "interpret":
        result = notebook.run(input_path)
        steps = ("open_notebook",)
    elif process == "proofread":
        result = languagetool.run(input_path)
        steps = ("languagetool",)
    else:
        result = office.run(input_path)
        steps = ("libreoffice",)

    return {"result": result, "trace": _trace(steps)}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    process, input_path = sys.argv[1:3]
    if process not in _ALLOWED:
        raise SystemExit("Process unavailable")
    inputs = {
        "input_path": str(Path(input_path).resolve()),
        "python": sys.executable,
        "powershell": str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"),
    }
    response = asyncio.run(execute(ROOT / "processes" / (process + ".yaml"), inputs))
    print(json.dumps(response, ensure_ascii=False))
