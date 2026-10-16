"""Minimal deterministic Front Door: data-driven rules, no authority."""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
import hashlib
import sqlite3
import threading

from nexus.contracts import ROOT, Blocked, strict_json, validate
from nexus.adapters.languagetool import correction_shadow
from nexus.capability_router import declared_router


_RULES = validate("frontdoor_rules", strict_json((ROOT / "frontdoor_rules.json").read_bytes()))
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



# The Markdown file is the local linguistic source of truth. Its digest is pinned
# inside this Host-sealed module: changing language rules requires review.
_PT_LANGUAGE_PATH = ROOT / "lingua" / "pt_PT.md"
_PT_LANGUAGE_SHA256 = "ff206eefcffa64c2d80e9d911f43abbc41f3704b920d4658e8306babcd95381f"
_PT_LANGUAGE_LOCK = threading.RLock()
_PT_ALLOWED_INTENTS = frozenset(
    ("arquivo", "web", "fontes", "trabalhar", "perguntar", "calcular")
)


def _pt_language_tables():
    raw = _PT_LANGUAGE_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != _PT_LANGUAGE_SHA256:
        raise Blocked("O dicionário ou a gramática portuguesa foram alterados.")
    markdown = raw.decode("utf-8")
    if markdown.count("<!-- nexus-pt-PT-v1 -->") != 1:
        raise Blocked("Fonte linguística incompatível.")
    try:
        lexicon = markdown.split("## Dicionário operacional\n", 1)[1].split(
            "\n## Gramática de cláusulas", 1
        )[0]
        grammar = markdown.split("<!-- nexus-pt-grammar-v1 -->", 1)[1].split(
            "<!-- /nexus-pt-grammar-v1 -->", 1
        )[0]
    except IndexError as error:
        raise Blocked("Tabelas linguísticas ausentes.") from error

    forms = {}
    entries = []
    for line in lexicon.splitlines():
        if not line.startswith("|"):
            continue
        values = [value.strip() for value in line.strip().strip("|").split("|")]
        if values[0] in {"forma", "---"}:
            continue
        if (len(values) != 3 or values[2] not in _PT_ALLOWED_INTENTS
                or not all(re.fullmatch(r"[a-záàâãéêíóôõúç]+", v) for v in values[:2])
                or values[0] in forms):
            raise Blocked("Entrada de dicionário inválida ou repetida.")
        forms[values[0]] = values[2]
        entries.append(tuple(values))
    if not 10 <= len(entries) <= 2000:
        raise Blocked("Dicionário operacional vazio ou excessivo.")

    grammar_map = {}
    for line in grammar.splitlines():
        if not line.startswith("|"):
            continue
        values = [value.strip() for value in line.strip().strip("|").split("|")]
        if values[0] in {"regra", "---"}:
            continue
        if len(values) != 2 or values[0] in grammar_map:
            raise Blocked("Regra de gramática portuguesa inválida.")
        expressions = tuple(part.strip() for part in values[1].split(";"))
        if (not expressions or any(not re.fullmatch(
                r"[a-záàâãéêíóôõúç ]{1,40}", part) for part in expressions)
                or len(set(expressions)) != len(expressions)):
            raise Blocked("Marcadores gramaticais inválidos.")
        grammar_map[values[0]] = expressions
    required = {"pergunta_inicio", "negacao_inicio", "segunda_acao", "segunda_clausula"}
    if set(grammar_map) != required:
        raise Blocked("Gramática portuguesa incompleta.")

    connection = sqlite3.connect(":memory:", check_same_thread=False)
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE pt_operational USING fts5("
            "form, lemma UNINDEXED, intent UNINDEXED, "
            "tokenize='unicode61 remove_diacritics 0')"
        )
        connection.executemany(
            "INSERT INTO pt_operational(form, lemma, intent) VALUES (?, ?, ?)", entries
        )
    except sqlite3.Error as error:
        connection.close()
        raise Blocked("Índice SQLite FTS5 português indisponível.") from error
    return connection, forms, grammar_map


_PT_LANGUAGE_DB, _PT_FORM_INTENTS, _PT_GRAMMAR = _pt_language_tables()
_PT_VERB_FORMS = {
    intent: frozenset(word for word, group in _PT_FORM_INTENTS.items()
                      if group == intent)
    for intent in _PT_ALLOWED_INTENTS
}


def _pt_lookup(word: str) -> tuple[str, ...]:
    """Exact FTS5 lookup. Vocabulary never grants a capability or permission."""
    if not re.fullmatch(r"[a-záàâãéêíóôõúç]{1,40}", word):
        return ()
    with _PT_LANGUAGE_LOCK:
        return tuple(row[0] for row in _PT_LANGUAGE_DB.execute(
            "SELECT DISTINCT intent FROM pt_operational "
            "WHERE form MATCH ? AND form = ?",
            ('"' + word + '"', word),
        ))


def _pt_markers(values: tuple[str, ...]) -> str:
    return "|".join(re.escape(value).replace(r"\ ", r"\s+")
                    for value in sorted(values, key=lambda item: (-len(item), item)))


_PT_QUESTION = re.compile(
    r"^(?:por favor[, ]+)?(?:"
    + "(?:" + _pt_markers(_PT_GRAMMAR["pergunta_inicio"]) + r")\b"
    + r"|(?:explica(?:-me)?|podes explicar|poderias explicar|"
      r"consegues explicar|diz-me|podes dizer-me)\s+como\b)"
)
_PT_ACTION_FORMS = sorted(
    set(_PT_FORM_INTENTS) | {"tema", "assunto"},
    key=lambda word: (-len(word), word)
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
    r"(?:(?:podes|poderias|pode|poderia|consegues|consegue|"
    r"quero que|preciso que|quero|pretendo|gostaria de|"
    r"preciso de|ajuda-me a)\s+)?"
    r"([a-záàâãéêíóôõúç-]+)\b"
)
_PT_WEB_TARGET = re.compile(r"\b(?:web|internet|online|net)\b")
_PT_SOURCE_TARGET = re.compile(r"\bfontes?\b")


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
