"""Deterministic front-door parsing for the Nexus Folha.

This module has no authority. It recognises explicit syntax and conservative
ELIZA-style natural-language patterns, returning only a candidate intent.
Kernel policy decides what can actually execute.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

from nexus.contracts import Blocked, strict_json, validate


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

# Conservative ELIZA-style pattern families. These rules classify intent only.
# They never choose a backend, permission, credential, Human Gate or authority.
NATURAL_RULES = {
    "arquivo": (
        r"\bguarda(?:r)?\b", r"\barquiva(?:r)?\b", r"\bsalva(?:r)?\b",
        r"\bguarda isto\b",
    ),
    "web": (
        r"\bpesquis[ae](?:r)?\b.*\b(?:web|internet|online|net)\b",
        r"\bprocura(?:r)?\b.*\b(?:web|internet|online|net)\b",
        r"\bpesquiza(?:r)?\b.*\b(?:web|internet|online|net)\b",
    ),
    "fontes": (
        r"\b(?:encontra|procura|pesquisa|pesquiza)\b.*\bfontes?\b",
        r"\bquais\b.*\bfontes?\b",
        r"\bda(?:-me)?\b.*\bfontes?\b",
    ),
    "trabalhar": (
        r"\btrabalha(?:r)?\b", r"\b(?:reve|revê|rever)\b", r"\bmelhora(?:r)?\b",
        r"\breescreve(?:r)?\b", r"\bcorrige(?:r)?\b",
    ),
    "perguntar": (
        r"\bexplica(?:r)?\b", r"\bresponde(?:r)?\b", r"\bo que (?:e|é)\b",
        r"\bquem (?:e|é)\b", r"\bporqu[eê]\b", r"\bcomo\b",
    ),
    "calcular": (
        r"\bcalcula(?:r)?\b", r"\bfaz(?:er)?\b.*\bconta\b",
        r"\bquanto (?:e|é)\b", r"\bsoma(?:r)?\b",
    ),
    "tema": (
        r"\btema\b", r"\bassunto\b", r"\bquero falar sobre\b",
    ),
}


@dataclass(frozen=True)
class ParsedInput:
    status: str
    intent: str | None
    original: str
    content: str
    parser: str
    explicit: bool
    shadow: str | None = None

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "intent": self.intent,
            "original": self.original,
            "content": self.content,
            "parser": self.parser,
            "explicit": self.explicit,
        }


def _normalise_for_matching(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\s+", " ", value).strip()


def parse_explicit(text: str) -> ParsedInput:
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if len(text) > MAX_TEXT_CHARS:
        return ParsedInput("BLOCKED", None, text, "", "prefix-v1", False)
    if any(ord(char) < 32 and char not in "\t\n\r" for char in text):
        return ParsedInput("BLOCKED", None, text, "", "prefix-v1", False)
    if not text.strip():
        return ParsedInput("UNRESOLVED", None, text, "", "prefix-v1", False)

    candidate = text.lstrip()
    for prefix, intent in PREFIXES:
        if candidate.startswith(prefix):
            content = candidate[len(prefix):].lstrip()
            if not content:
                return ParsedInput("UNRESOLVED", intent, text, "", "prefix-v1", True)
            return ParsedInput("RESOLVED", intent, text, content, "prefix-v1", True)

    return ParsedInput("UNRESOLVED", None, text, text, "prefix-v1", False)


def parse_natural(text: str) -> ParsedInput:
    explicit = parse_explicit(text)
    if explicit.status != "UNRESOLVED" or explicit.explicit:
        return explicit

    normal = _normalise_for_matching(text)
    matches = []
    for intent, patterns in NATURAL_RULES.items():
        if any(re.search(pattern, normal) for pattern in patterns):
            matches.append(intent)

    # More than one plausible intent is deliberately left unresolved.
    if len(matches) != 1:
        return ParsedInput("UNRESOLVED", None, text, text, "eliza-rules-v1", False)

    return ParsedInput("RESOLVED", matches[0], text, text, "eliza-rules-v1", False)


def parse(text: str) -> ParsedInput:
    """Public front-door parser: explicit prefix first, natural rules second."""
    return parse_natural(text)



def _parse_natural_rules(text: str, *, original: str | None = None, parser: str = "eliza-rules-v1",
                         shadow: str | None = None) -> ParsedInput:
    normal = _normalise_for_matching(text)
    matches = []
    for intent, patterns in NATURAL_RULES.items():
        if any(re.search(pattern, normal) for pattern in patterns):
            matches.append(intent)
    source = text if original is None else original
    if len(matches) != 1:
        return ParsedInput("UNRESOLVED", None, source, source, parser, False, shadow)
    return ParsedInput("RESOLVED", matches[0], source, source, parser, False, shadow)


def languagetool_shadow(text: str, raw) -> str:
    """Apply only unambiguous LanguageTool replacements to a non-authoritative shadow.

    The original is never changed. Invalid or overlapping diagnostics are rejected
    so LanguageTool cannot silently manufacture a command.
    """
    value = strict_json(raw) if isinstance(raw, (str, bytes, bytearray)) else raw
    validate("languagetool", value)
    if value["warnings"]["incompleteResults"]:
        raise Blocked("LanguageTool devolveu resultados incompletos.")

    edits = []
    for match in value["matches"]:
        offset = match.get("offset")
        length = match.get("length")
        replacements = match.get("replacements", [])
        if not isinstance(offset, int) or isinstance(offset, bool) or not isinstance(length, int) or isinstance(length, bool):
            continue
        if offset < 0 or length <= 0 or offset + length > len(text):
            raise Blocked("LanguageTool devolveu posições inválidas.")
        # Multiple alternatives are semantically ambiguous: do not guess.
        if len(replacements) != 1:
            continue
        replacement = replacements[0].get("value")
        if not isinstance(replacement, str) or len(replacement) > 200 or any(ord(ch) < 32 for ch in replacement):
            continue
        edits.append((offset, offset + length, replacement))

    edits.sort()
    for previous, current in zip(edits, edits[1:]):
        if current[0] < previous[1]:
            raise Blocked("LanguageTool devolveu correções sobrepostas.")

    shadow = text
    for start, end, replacement in reversed(edits):
        shadow = shadow[:start] + replacement + shadow[end:]
    return shadow


def parse_with_languagetool(text: str, raw) -> ParsedInput:
    """Retry unresolved Portuguese through a LanguageTool correction shadow."""
    first = parse(text)
    if first.status != "UNRESOLVED" or first.explicit:
        return first
    try:
        shadow = languagetool_shadow(text, raw)
    except (Blocked, TypeError, ValueError, KeyError):
        return first
    if shadow == text:
        return first
    # Never treat a LanguageTool-created prefix as explicit authority.
    return _parse_natural_rules(
        shadow,
        original=text,
        parser="languagetool-shadow+eliza-v1",
        shadow=shadow,
    )
