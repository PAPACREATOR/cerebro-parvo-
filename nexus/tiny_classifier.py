"""Bounded local tiny-model intent classifier.

The tiny model only returns one of seven Nexus intents or UNKNOWN. It receives
the human text plus a fixed instruction and has no tools, files, Store or
Canonical capability.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from nexus.contracts import Blocked, strict_json

INTENTS = ("arquivo", "web", "fontes", "trabalhar", "perguntar", "calcular", "tema")


@dataclass(frozen=True)
class TinySpec:
    executable: str
    args: tuple[str, ...]
    timeout: int = 30


def classify(text: str, spec: TinySpec) -> list[str]:
    if not isinstance(text, str) or not text.strip() or len(text) > 4000:
        raise Blocked("Texto inválido para tiny classifier.")
    executable = Path(spec.executable)
    if not executable.is_absolute() or not executable.is_file():
        raise Blocked("Tiny local indisponível.")

    prompt = {
        "task": "classify_nexus_intent",
        "allowed": list(INTENTS),
        "rules": [
            "Return exactly one JSON object.",
            "Use intent UNKNOWN when more than one interpretation is plausible.",
            "Never return approval, process, tool, path, command or authority.",
        ],
        "text": text,
    }
    try:
        result = subprocess.run(
            [str(executable), *spec.args],
            input=json.dumps(prompt, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=spec.timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Blocked("Tiny local indisponível.") from error

    if result.returncode != 0 or len(result.stdout.encode("utf-8", errors="replace")) > 20_000:
        raise Blocked("Tiny local falhou.")

    value = strict_json(result.stdout)
    if not isinstance(value, dict) or set(value) != {"intent"}:
        raise Blocked("Tiny devolveu contrato inválido.")
    intent = value["intent"]
    if intent == "UNKNOWN":
        return []
    if intent not in INTENTS:
        raise Blocked("Tiny devolveu intenção proibida.")
    return [intent]
