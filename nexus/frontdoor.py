"""Minimal deterministic front door for the Nexus Folha.

No authority lives here. The module recognises explicit syntax, conservative
ELIZA-style intent patterns and an optional LanguageTool correction shadow.
Kernel policy alone decides what can execute.
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

# Small deterministic command vocabulary, not a translator.
# PT first; EN/FR aliases only cover common Nexus commands.
NATURAL_RULES = {
    "arquivo": (
        r"\bguarda(?:r)?\b", r"\barquiva(?:r)?\b", r"\bsalva(?:r)?\b",
        r"\bsave\b", r"\barchive\b", r"\bstore\b",
        r"\bsauvegarde(?:r)?\b", r"\barchive(?:r)?\b", r"\benregistre(?:r)?\b",
    ),
    "web": (
        r"\bpesquis[ae](?:r)?\b.*\b(?:web|internet|online|net)\b",
        r"\bprocura(?:r)?\b.*\b(?:web|internet|online|net)\b",
        r"\bpesquiza(?:r)?\b.*\b(?:web|internet|online|net)\b",
        r"\b(?:search|look up|find)\b.*\b(?:web|internet|online)\b",
        r"\b(?:cherche|recherche|trouve)\b.*\b(?:web|internet|en ligne)\b",
    ),
    "fontes": (
        r"\b(?:encontra|procura|pesquisa|pesquiza)\b.*\bfontes?\b",
        r"\bquais\b.*\bfontes?\b", r"\bda(?:-me)?\b.*\bfontes?\b",
        r"\b(?:find|search|give me)\b.*\bsources?\b",
        r"\b(?:trouve|cherche|recherche|donne-moi)\b.*\bsources?\b",
    ),
    "trabalhar": (
        r"\btrabalha(?:r)?\b", r"\b(?:reve|revê|rever)\b", r"\bmelhora(?:r)?\b",
        r"\breescreve(?:r)?\b", r"\bcorrige(?:r)?\b",
        r"\b(?:revise|rewrite|improve|correct|edit)\b",
        r"\b(?:revise|révise|revoir|ameliore|améliore|reecris|réécris|corrige)\b",
    ),
    "perguntar": (
        r"\bexplica(?:r)?\b", r"\bresponde(?:r)?\b", r"\bo que (?:e|é)\b",
        r"\bquem (?:e|é)\b", r"\bporqu[eê]\b", r"\bcomo\b",
        r"\bexplain\b", r"\bwhat is\b", r"\bwho is\b", r"\bwhy\b", r"\bhow\b",
        r"\bexplique\b", r"\bqu['’]est-ce que\b", r"\bqui est\b",
        r"\bpourquoi\b", r"\bcomment\b",
    ),
    "calcular": (
        r"\bcalcula(?:r)?\b", r"\bfaz(?:er)?\b.*\bconta\b",
        r"\bquanto (?:e|é)\b", r"\bsoma(?:r)?\b",
        r"\b(?:calculate|compute|sum)\b", r"\bhow much is\b",
        r"\b(?:calcule|calculer|somme)\b", r"\bcombien (?:fait|font|est)\b",
    ),
    "tema": (
        r"\btema\b", r"\bassunto\b", r"\bquero falar sobre\b",
        r"\btopic\b", r"\bsubject\b", r"\btalk about\b",
        r"\btheme\b", r"\bthème\b", r"\bsujet\b", r"\bparler de\b",
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
        value = {
            "status": self.status,
            "intent": self.intent,
            "original": self.original,
            "content": self.content,
            "parser": self.parser,
            "explicit": self.explicit,
        }
        if self.shadow is not None:
            value["shadow"] = self.shadow
        return value


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()


def _match_natural(
    text: str,
    *,
    original: str | None = None,
    parser: str = "eliza-rules-v1",
    shadow: str | None = None,
) -> ParsedInput:
    matches = [
        intent
        for intent, patterns in NATURAL_RULES.items()
        if any(re.search(pattern, _normalise(text)) for pattern in patterns)
    ]
    source = text if original is None else original
    if len(matches) != 1:
        return ParsedInput("UNRESOLVED", None, source, source, parser, False, shadow)
    return ParsedInput("RESOLVED", matches[0], source, source, parser, False, shadow)


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


def parse(text: str) -> ParsedInput:
    explicit = parse_explicit(text)
    if explicit.status != "UNRESOLVED" or explicit.explicit:
        return explicit
    return _match_natural(text)


def languagetool_shadow(text: str, raw) -> str:
    """Apply only unambiguous LanguageTool replacements to a non-authoritative shadow."""
    value = strict_json(raw) if isinstance(raw, (str, bytes, bytearray)) else raw
    validate("languagetool", value)
    if value["warnings"]["incompleteResults"]:
        raise Blocked("LanguageTool devolveu resultados incompletos.")

    edits = []
    for match in value["matches"]:
        offset = match.get("offset")
        length = match.get("length")
        replacements = match.get("replacements", [])
        if not isinstance(offset, int) or isinstance(offset, bool):
            continue
        if not isinstance(length, int) or isinstance(length, bool):
            continue
        if offset < 0 or length <= 0 or offset + length > len(text):
            raise Blocked("LanguageTool devolveu posições inválidas.")
        if len(replacements) != 1:
            continue
        replacement = replacements[0].get("value")
        if not isinstance(replacement, str) or len(replacement) > 200:
            continue
        if any(ord(char) < 32 for char in replacement):
            continue
        edits.append((offset, offset + length, replacement))

    edits.sort()
    if any(current[0] < previous[1] for previous, current in zip(edits, edits[1:])):
        raise Blocked("LanguageTool devolveu correções sobrepostas.")

    shadow = text
    for start, end, replacement in reversed(edits):
        shadow = shadow[:start] + replacement + shadow[end:]
    return shadow


def parse_with_languagetool(text: str, raw) -> ParsedInput:
    """Retry only unresolved text through a validated, non-authoritative correction shadow."""
    first = parse(text)
    if first.status != "UNRESOLVED" or first.explicit:
        return first
    try:
        shadow = languagetool_shadow(text, raw)
    except (Blocked, TypeError, ValueError, KeyError):
        return first
    if shadow == text:
        return first
    # A correction may improve natural-language matching but can never create
    # explicit-prefix authority.
    return _match_natural(
        shadow,
        original=text,
        parser="languagetool-shadow+eliza-v1",
        shadow=shadow,
    )
