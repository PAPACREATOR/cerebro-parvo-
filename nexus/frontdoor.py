"""Deterministic front-door parsing for the Nexus Folha.

This module has no authority. It only recognises explicit user syntax and
returns a candidate intent. Kernel policy decides what can actually execute.
"""
from __future__ import annotations

from dataclasses import dataclass


PREFIXES = (
    ("@@", "arquivo"),
    ('""', "fontes"),
    ("??", "perguntar"),
    ("&", "trabalhar"),
    ("%", "calcular"),
    ("#", "tema"),
    ("@", "web"),
)

MAX_TEXT_CHARS = 100_000


@dataclass(frozen=True)
class ParsedInput:
    status: str
    intent: str | None
    original: str
    content: str
    parser: str
    explicit: bool

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "intent": self.intent,
            "original": self.original,
            "content": self.content,
            "parser": self.parser,
            "explicit": self.explicit,
        }


def parse_explicit(text: str) -> ParsedInput:
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if len(text) > MAX_TEXT_CHARS:
        return ParsedInput("BLOCKED", None, text, "", "prefix-v1", False)
    if not text.strip():
        return ParsedInput("UNRESOLVED", None, text, "", "prefix-v1", False)

    # Leading horizontal/vertical whitespace is presentation, not authority.
    # The literal original is never changed.
    candidate = text.lstrip()
    for prefix, intent in PREFIXES:
        if candidate.startswith(prefix):
            content = candidate[len(prefix):].lstrip()
            if not content:
                return ParsedInput("UNRESOLVED", intent, text, "", "prefix-v1", True)
            return ParsedInput("RESOLVED", intent, text, content, "prefix-v1", True)

    return ParsedInput("UNRESOLVED", None, text, text, "prefix-v1", False)
