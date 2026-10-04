"""Natural language -> internal Markdown -> bounded Kernel handoff.

The Markdown header carries no authority. It only binds the ELIZA parse to the
exact human text. Kernel/Store remain the authority for IDs, state, provenance
and Human Gate.
"""
from __future__ import annotations

import hashlib
import json
import re

from nexus.contracts import Blocked
from nexus.frontdoor import ParsedInput, parse
from nexus.adapters.notebook import prepare_source

HEADER_RE = re.compile(r"\A<!-- nexus-natural-v1 (\{[^\n]*\}) -->\n", re.ASCII)
INTENTS = {"arquivo", "web", "fontes", "trabalhar", "perguntar", "calcular", "tema"}


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def to_markdown(value: str | ParsedInput) -> str:
    parsed = parse(value) if isinstance(value, str) else value
    if not isinstance(parsed, ParsedInput):
        raise TypeError("value must be text or ParsedInput")
    if parsed.status != "RESOLVED" or parsed.intent not in INTENTS:
        raise Blocked("A intenção humana ainda não está resolvida.")
    meta = {
        "version": 1,
        "intent": parsed.intent,
        "parser": parsed.parser,
        "explicit": parsed.explicit,
        "sha256": _digest(parsed.original),
    }
    header = json.dumps(meta, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "<!-- nexus-natural-v1 " + header + " -->\n" + parsed.original


def from_markdown(markdown: str) -> dict:
    if not isinstance(markdown, str):
        raise TypeError("markdown must be str")
    match = HEADER_RE.match(markdown)
    if match is None:
        raise Blocked("Markdown interno sem cabeçalho Nexus válido.")
    try:
        meta = json.loads(match.group(1))
    except (ValueError, TypeError) as error:
        raise Blocked("Cabeçalho Nexus inválido.") from error
    if not isinstance(meta, dict) or set(meta) != {"version", "intent", "parser", "explicit", "sha256"}:
        raise Blocked("Cabeçalho Nexus inválido.")
    if meta["version"] != 1 or meta["intent"] not in INTENTS:
        raise Blocked("Cabeçalho Nexus incompatível.")
    if not isinstance(meta["parser"], str) or not meta["parser"] or len(meta["parser"]) > 100:
        raise Blocked("Parser Nexus inválido.")
    if type(meta["explicit"]) is not bool:
        raise Blocked("Marca de intenção explícita inválida.")
    original = markdown[match.end():]
    if _digest(original) != meta["sha256"]:
        raise Blocked("O texto humano mudou depois da interpretação.")
    return {"intent": meta["intent"], "parser": meta["parser"], "explicit": meta["explicit"], "text": original}


def kernel_to_notebook(markdown: str) -> dict:
    """Validate ELIZA Markdown and prepare exact human text for Notebook."""
    packet = from_markdown(markdown)
    source = prepare_source(packet["text"].encode("utf-8"))
    return {
        "intent": packet["intent"],
        "parser": packet["parser"],
        "explicit": packet["explicit"],
        "input_text": source,
        "input_sha256": _digest(source),
        "target": "open-notebook",
        "authority": "UNTRUSTED_REQUEST",
    }
