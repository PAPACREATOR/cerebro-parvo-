"""Deterministic Nexus process runner. No workflow engine and no AI authority."""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from nexus.contracts import Blocked, ROOT
from nexus.adapters.tools import hash_python, compare, report
from nexus.adapters.notebook import run as run_notebook
from nexus.adapters.languagetool import run as run_languagetool
from nexus.adapters.office import run as run_office
from nexus.adapters.constitutional import read_object

VERIFY_POLICY = {
    "agreement": "PASS",
    "conflict": "UNKNOWN",
    "unknown": "UNKNOWN",
    "failure": "FAIL",
}


def _powershell():
    root = os.environ.get("SystemRoot") or os.environ.get("WINDIR")
    if not root:
        raise Blocked("PowerShell Windows indisponível.")
    return str(Path(root) / "System32/WindowsPowerShell/v1.0/powershell.exe")


def hash_windows(path):
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
            [_powershell(), "-NoProfile", "-NonInteractive", "-Command", script],
            input=str(Path(path).resolve()),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise Blocked("A verificação Windows falhou ou excedeu o tempo permitido.") from None
    if completed.returncode != 0 or not completed.stdout.strip():
        raise Blocked("A verificação Windows não devolveu um resultado utilizável.")
    try:
        value = json.loads(completed.stdout.strip().splitlines()[-1])
    except (ValueError, UnicodeError):
        raise Blocked("A verificação Windows devolveu dados inválidos.") from None
    if not isinstance(value, dict) or value.get("status") not in ("PASS", "FAIL"):
        raise Blocked("A verificação Windows devolveu um contrato inválido.")
    return value


def _trace(steps):
    return {
        "engine": "nexus/python",
        "version": "1.0.0",
        "summary": {
            "usage": {"total_tokens": 0},
            "agents_executed": list(steps),
        },
        "events": [{"type": "step.completed", "step": name} for name in steps],
    }


def execute(process, input_path):
    path = Path(input_path)
    if process == "verify":
        a = hash_windows(path)
        b = hash_python(path)
        compared = compare(a, b)
        result = report({"comparison": compared, "status": VERIFY_POLICY[compared["outcome"]]})
        return {"result": result, "trace": _trace(("hash_windows", "hash_python", "compare", "report"))}
    if process == "interpret":
        return {"result": run_notebook(path), "trace": _trace(("open_notebook",))}
    if process == "proofread":
        return {"result": run_languagetool(path), "trace": _trace(("languagetool",))}
    if process == "convert_pdf":
        return {"result": run_office(path), "trace": _trace(("libreoffice",))}
    if process == "register_object":
        return {"result": read_object(path), "trace": _trace(("read_object",))}
    raise Blocked("Processo indisponível.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        process, input_path = sys.argv[1:3]
        print(json.dumps(execute(process, input_path), ensure_ascii=False))
    except Exception:
        print("Execução determinística indisponível ou resposta rejeitada.", file=sys.stderr)
        raise SystemExit(1)
