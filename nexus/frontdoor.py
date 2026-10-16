"""Minimal deterministic Front Door: data-driven rules, no authority."""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
import hashlib

from nexus.contracts import ROOT, Blocked, strict_json, validate
from nexus.adapters.languagetool import correction_shadow
from nexus.capability_router import declared_router


# Only a pinned Python parser may interpret the pinned Markdown corpus.
# Both digests live in this Host-sealed module. Fail closed on tampering.
_PT_LANGUAGE_PATH = ROOT / "lingua" / "pt_PT.md"
_PT_LANGUAGE_SHA256 = "3ac567d93a6276bc3cefba399e7389b9f07782e598518508ec2b104ec2d6d90b"
_PT_INDEXER_PATH = ROOT / "lingua" / "indexer.py"
_PT_INDEXER_SHA256 = "8a1e3615f9fbec2f70a6862d8b30cae7a75152d598e64e2de12a869ee672ab1a"
if (_PT_INDEXER_PATH.is_symlink()
        or hashlib.sha256(_PT_INDEXER_PATH.read_bytes()).hexdigest() != _PT_INDEXER_SHA256):
    raise Blocked("O indexador português foi alterado sem revisão.")

from nexus.lingua.indexer import load_corpus

_PT_CORPUS = load_corpus(_PT_LANGUAGE_PATH, _PT_LANGUAGE_SHA256)
_LEGACY_RULES = validate("frontdoor_rules", strict_json(
    (ROOT / "frontdoor_rules.json").read_bytes()
))
_RULES = validate("frontdoor_rules", _PT_CORPUS.rules)
if _RULES != _LEGACY_RULES:
    raise Blocked("Regras Markdown e contrato histórico divergem.")
PREFIXES = tuple((item[0], item[1]) for item in _RULES["prefixes"])
NATURAL_RULES = _RULES["natural_rules"]
CLARIFICATION_PATTERNS = _RULES["clarification_patterns"]
OPERATION_RULES = _RULES["operation_rules"]
MAX_TEXT_CHARS = _RULES["max_text_chars"]


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



# All lexical forms, clause markers, prefixes, and natural rules are loaded
# from the same reviewed Markdown. This is advisory interpretation only.
_PT_LANGUAGE_DB = _PT_CORPUS.connection
_PT_FORM_INTENTS = _PT_CORPUS.forms
_PT_GRAMMAR = _PT_CORPUS.grammar
_PT_VERB_FORMS = {
    intent: frozenset(form for form, group in _PT_FORM_INTENTS.items()
                      if group == intent)
    for intent in ("arquivo", "web", "fontes", "trabalhar", "perguntar", "calcular")
}
_pt_lookup = _PT_CORPUS.lookup
_pt_search = _PT_CORPUS.search


def _pt_markers(values: tuple[str, ...]) -> str:
    return "|".join(re.escape(value).replace(r"\ ", r"\s+")
                    for value in sorted(values, key=lambda item: (-len(item), item)))


_PT_QUESTION = re.compile(
    r"^(?:por favor[, ]+)?(?:"
    + "(?:" + _pt_markers(_PT_GRAMMAR["pergunta_inicio"]) + r")\b"
    + "|(?:" + _pt_markers(_PT_GRAMMAR["pergunta_modal"]) + r")\s+como\b)"
)
_PT_ACTION_FORMS = sorted(
    set(_PT_FORM_INTENTS) | {"tema", "assunto"}, key=lambda w: (-len(w), w)
)
_PT_SEPARATE_ACTION = re.compile(
    r"\b(?:" + _pt_markers(_PT_GRAMMAR["segunda_acao"]) + r")\s+(?:"
    + "|".join(re.escape(word) for word in _PT_ACTION_FORMS)
    + r"|quero\s+falar\s+sobre)\b"
)
_PT_SECOND_CLAUSE = re.compile(
    r"\b(?:" + _pt_markers(_PT_GRAMMAR["segunda_clausula"]) + r")\b"
)
_PT_NEGATIVE_HEAD = re.compile(
    r"^(?:por favor[, ]+)?(?:"
    + _pt_markers(_PT_GRAMMAR["negacao_inicio"]) + r")\b"
)
_PT_VERB_HEAD = re.compile(
    r"^(?:por favor[, ]+)?"
    r"(?:(?:" + _pt_markers(_PT_GRAMMAR["pedido_modal"]) + r")\s+)?"
    r"([a-záàâãéêíóôõúç-]+)\b"
)
_PT_WEB_TARGET = re.compile(
    r"\b(?:" + _pt_markers(_PT_GRAMMAR["contexto_web"]) + r")\b"
)
_PT_SOURCE_TARGET = re.compile(
    r"\b(?:" + _pt_markers(_PT_GRAMMAR["contexto_fontes"]) + r")\b"
)


def _pt_grammar_intent(normal: str) -> str | None:
    """Compare one Portuguese grammatical head with a small verb dictionary.

    Tokens after 'como' in a method question do not become actions.
    Negation and genuine separate instructions are never resolved here.
    Only a single safe intent is returned, never a process ID or authority.
    """
    if len(normal) > 12000 or _PT_NEGATIVE_HEAD.match(normal):
        return None
    if _PT_QUESTION.match(normal):
        return ("perguntar" if not _PT_SEPARATE_ACTION.search(normal)
                and not _PT_SECOND_CLAUSE.search(normal) else None)
    head = _PT_VERB_HEAD.match(normal)
    if (head is None or _PT_SEPARATE_ACTION.search(normal)
            or _PT_SECOND_CLAUSE.search(normal)):
        return None
    verb = head.group(1)
    matches = []
    for intent in _pt_lookup(verb):
        if intent == "web":
            if _PT_SOURCE_TARGET.search(normal):
                matches.append("fontes")
            elif _PT_WEB_TARGET.search(normal):
                matches.append("web")
        elif intent == "fontes":
            if _PT_SOURCE_TARGET.search(normal):
                matches.append(intent)
        else:
            matches.append(intent)
    return matches[0] if len(set(matches)) == 1 else None


def _explanation_is_primary(normal: str, intents: list[str]) -> bool:
    """Portuguese main-clause hint, without execution authority.

    'Explica como guardar' is a question; 'explica ... e depois guarda'
    contains a separate imperative and must ask for human clarification.
    """
    return ("perguntar" in intents and _PT_QUESTION.match(normal) is not None
            and _pt_grammar_intent(normal) == "perguntar")


def requires_clarification(text: str) -> bool:
    """Refusals, citations and separate main actions remain with the human."""
    normal = _normalise(text)
    if any(re.search(pattern, normal) for pattern in CLARIFICATION_PATTERNS):
        return True
    intents = [intent for intent, patterns in NATURAL_RULES.items()
               if any(re.search(pattern, normal) for pattern in patterns)]
    return len(intents) > 1 and not _explanation_is_primary(normal, intents)


def _natural(text: str, *, original: str | None = None, parser="eliza-rules-v1",
             shadow: str | None = None) -> ParsedInput:
    normal = _normalise(text)
    matches = [
        intent for intent, patterns in NATURAL_RULES.items()
        if any(re.search(pattern, normal) for pattern in patterns)
    ]
    source = text if original is None else original
    grammar_intent = _pt_grammar_intent(normal)
    if grammar_intent == "perguntar" and _PT_QUESTION.match(normal):
        matches = ["perguntar"]
    elif not matches and grammar_intent is not None:
        matches = [grammar_intent]
    if not matches and not requires_clarification(source) and not requires_clarification(text):
        try:
            candidate = declared_router().recognise_command(text)
        except (Blocked, ValueError):
            candidate = None
        if candidate is not None:
            matches = [candidate.intent]
    if len(matches) != 1 or requires_clarification(source) or requires_clarification(text):
        return ParsedInput("UNRESOLVED", None, source, source, parser, False, shadow)
    return ParsedInput("RESOLVED", matches[0], source, source, parser, False, shadow)



def propose_operation(parsed: ParsedInput, *, filename: str, attachment: str) -> str | None:
    """Return one explicitly configured process proposal; never execute it."""
    if type(parsed) is not ParsedInput or parsed.status != "RESOLVED":
        return None
    if not isinstance(filename, str) or not isinstance(attachment, str):
        return None
    normal = _normalise(parsed.content)
    matches = []
    for rule in OPERATION_RULES:
        if rule["intent"] != parsed.intent:
            continue
        if rule["requires_attachment"] and (not filename or not attachment):
            continue
        if any(re.search(pattern, normal) for pattern in rule["patterns"]):
            matches.append(rule["process"])
    return matches[0] if len(matches) == 1 else None

def parse_explicit(text: str) -> ParsedInput:
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if len(text) > MAX_TEXT_CHARS or any((ord(c) < 32 and c not in "\t\n\r") or 127 <= ord(c) < 160 for c in text):
        return ParsedInput("BLOCKED", None, text, "", "prefix-v1", False)
    if not text.strip():
        return ParsedInput("UNRESOLVED", None, text, "", "prefix-v1", False)

    candidate = text.lstrip()
    for prefix, intent in PREFIXES:
        if candidate.startswith(prefix):
            content = candidate[len(prefix):].lstrip()
            return ParsedInput(
                "RESOLVED" if content else "UNRESOLVED",
                intent,
                text,
                content,
                "prefix-v1",
                True,
            )
    return ParsedInput("UNRESOLVED", None, text, text, "prefix-v1", False)


def parse(text: str) -> ParsedInput:
    explicit = parse_explicit(text)
    if explicit.status != "UNRESOLVED" or explicit.explicit:
        return explicit
    return _natural(text)


def parse_with_languagetool(text: str, raw) -> ParsedInput:
    first = parse(text)
    if first.status != "UNRESOLVED" or first.explicit or requires_clarification(text):
        return first
    try:
        shadow = correction_shadow(text, raw)
    except (Blocked, TypeError, ValueError, KeyError):
        return first
    if shadow == text:
        return first
    return _natural(
        shadow,
        original=text,
        parser="languagetool-shadow+eliza-v1",
        shadow=shadow,
    )
