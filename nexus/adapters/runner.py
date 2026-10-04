"""Minimal deterministic Nexus executor.

No workflow engine. Dispatches only the four Host-authorized processes to the
already-tested Nexus adapters. Authority, persistence, recovery and Human Gate
remain in Host/Store.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from nexus.adapters.verify_direct import execute as verify
from nexus.adapters.notebook import run as interpret
from nexus.adapters.languagetool import run as proofread
from nexus.adapters.office import run as convert_pdf
from nexus.contracts import Blocked


def _trace(process, steps):
    return {
        "engine": "nexus/python-direct",
        "version": "1.0.0",
        "process": process,
        "summary": {
            "usage": {"total_tokens": 0},
            "agents_executed": list(steps),
        },
        "events": [{"type": "step.completed", "step": step} for step in steps],
    }


def execute(process, input_path):
    path = Path(input_path).resolve()
    if process == "verify":
        response = verify(path)
        return {
            "result": response["result"],
            "trace": _trace(process, ("hash_windows", "hash_python", "compare", "report")),
        }
    if process == "interpret":
        return {"result": interpret(path), "trace": _trace(process, ("open_notebook",))}
    if process == "proofread":
        return {"result": proofread(path), "trace": _trace(process, ("languagetool",))}
    if process == "convert_pdf":
        return {"result": convert_pdf(path), "trace": _trace(process, ("libreoffice",))}
    raise Blocked("Processo indisponível.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        process, input_path = sys.argv[1:3]
        print(json.dumps(execute(process, input_path), ensure_ascii=False))
    except Exception:
        print("Execução determinística indisponível ou resposta rejeitada.", file=sys.stderr)
        raise SystemExit(1)
