"""Markdown PT-PT -> deterministic clauses and SQLite FTS5 (advisory only)."""
from __future__ import annotations

import hashlib
import re
import sqlite3
import threading
from pathlib import Path

from nexus.contracts import Blocked, strict_json

INTENTS = frozenset(("arquivo", "web", "fontes", "trabalhar", "perguntar", "calcular"))
REQUIRED_GRAMMAR = frozenset((
    "pergunta_inicio", "negacao_inicio", "segunda_acao", "segunda_clausula",
    "pergunta_modal", "pedido_modal", "contexto_web", "contexto_fontes",
))
WORD = re.compile(r"[a-záàâãéêíóôõúç]{1,40}\Z")
MARKER = re.compile(r"[a-záàâãéêíóôõúç\- ]{1,60}\Z")


def _section(markdown: str, start: str, end: str) -> str:
    if markdown.count(start) != 1 or markdown.count(end) != 1:
        raise Blocked("Secção do cofre linguístico ausente ou ambígua.")
    body = markdown.split(start, 1)[1].split(end, 1)[0]
    if not body.strip():
        raise Blocked("Secção linguística vazia.")
    return body


def _table(body: str, *, columns: int):
    items = []
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        if len(cells) != columns:
            raise Blocked("Tabela Markdown com número de colunas incorreto.")
        if cells[0] in {"forma", "regra"} or all(set(v) <= {"-", " "} for v in cells):
            continue
        items.append(cells)
    return items


class LanguageIndex:
    """Verified corpus, a runtime FTS5 cache and no execution authority."""

    def __init__(self, markdown: str, sha256: str):
        self.sha256 = sha256
        vocab = _section(
            markdown, "## Dicionário operacional\n", "\n## Gramática de cláusulas"
        )
        entries = _table(vocab, columns=3)
        if not 10 <= len(entries) <= 2000:
            raise Blocked("Dimensão do léxico operacional inválida.")
        forms = {}
        for form, lemma, intent in entries:
            if (not WORD.fullmatch(form) or not WORD.fullmatch(lemma)
                    or intent not in INTENTS or form in forms):
                raise Blocked("Léxico operacional inválido ou repetido.")
            forms[form] = intent
        self.forms = forms
        raw_grammar = _section(
            markdown, "<!-- nexus-pt-grammar-v1 -->",
            "<!-- /nexus-pt-grammar-v1 -->"
        )
        grammar = {}
        for name, words in _table(raw_grammar, columns=2):
            if name in grammar or name not in REQUIRED_GRAMMAR:
                raise Blocked("Regra de gramática inexistente ou repetida.")
            choices = tuple(item.strip() for item in words.split(";"))
            if (not choices or len(choices) > 40
                    or any(not MARKER.fullmatch(c) for c in choices)
                    or len(set(choices)) != len(choices)):
                raise Blocked("Marcadores de gramática inválidos.")
            grammar[name] = choices
        if set(grammar) != REQUIRED_GRAMMAR:
            raise Blocked("Gramática incompleta.")
        self.grammar = grammar
        raw_contract = _section(
            markdown, "<!-- nexus-frontdoor-contract-v1 -->\n~~~json\n",
            "\n~~~\n<!-- /nexus-frontdoor-contract-v1 -->"
        )
        self.rules = strict_json(raw_contract)
        if not isinstance(self.rules, dict):
            raise Blocked("Contrato linguístico inválido.")
        # Every byte of large chapters remains searchable. Split at a word
        # boundary where possible; never silently drop the last pages.
        chapters = []
        chapter = None

        def add_chapter(part):
            if part is None:
                return
            content = "\n".join(part[1])
            start = 0
            while start < len(content):
                end = min(start + 16_000, len(content))
                if end < len(content):
                    boundary = max(content.rfind(" ", start, end),
                                   content.rfind("\n", start, end))
                    if boundary > start + 8_000:
                        end = boundary + 1
                chapters.append((part[0], content[start:end]))
                start = end

        for line in markdown.splitlines():
            if line.startswith("## "):
                add_chapter(chapter)
                chapter = (line[3:].strip(), [])
            elif chapter and not line.startswith("<!-- "):
                chapter[1].append(line)
        add_chapter(chapter)
        if len(chapters) > 2000:
            raise Blocked("Demasiados blocos no cofre linguístico.")

        self.lock = threading.RLock()
        self.connection = sqlite3.connect(":memory:", check_same_thread=False)
        try:
            self.connection.execute(
                "CREATE VIRTUAL TABLE pt_operational USING fts5("
                "form, lemma UNINDEXED, intent UNINDEXED,"
                " tokenize='unicode61 remove_diacritics 0')"
            )
            self.connection.executemany(
                "INSERT INTO pt_operational(form,lemma,intent) VALUES (?,?,?)",
                entries
            )
            self.connection.execute(
                "CREATE VIRTUAL TABLE pt_passages USING fts5("
                "title, body, tokenize='unicode61 remove_diacritics 0')"
            )
            self.connection.executemany(
                "INSERT INTO pt_passages(title,body) VALUES (?,?)", chapters
            )
        except sqlite3.Error as error:
            self.connection.close()
            raise Blocked("FTS5 português local indisponível.") from error

    def lookup(self, word: str) -> tuple[str, ...]:
        """FTS5 exact phrase + equality; no fuzzy command/authority inference."""
        if type(word) is not str or not WORD.fullmatch(word):
            return ()
        try:
            with self.lock:
                return tuple(row[0] for row in self.connection.execute(
                    "SELECT DISTINCT intent FROM pt_operational "
                    "WHERE form MATCH ? AND form = ?",
                    ('"' + word + '"', word)
                ))
        except sqlite3.Error as error:
            raise Blocked("Consulta ao índice local falhou.") from error

    def search(self, query: str, limit: int = 5) -> tuple[dict, ...]:
        """Full-text evidence only, never permission or a process proposal."""
        if (type(query) is not str or type(limit) is not int
                or not 1 <= limit <= 10 or len(query) > 200):
            raise Blocked("Pesquisa linguística inválida.")
        tokens = re.findall(r"[a-záàâãéêíóôõúç]{2,40}", query.casefold())
        if not 1 <= len(tokens) <= 8:
            return ()
        expression = " AND ".join('"' + token + '"' for token in tokens)
        try:
            with self.lock:
                rows = self.connection.execute(
                    "SELECT title, substr(body,1,400) FROM pt_passages "
                    "WHERE pt_passages MATCH ? ORDER BY bm25(pt_passages) LIMIT ?",
                    (expression, limit)
                ).fetchall()
        except sqlite3.Error as error:
            raise Blocked("Pesquisa linguística indisponível.") from error
        return tuple({
            "title": title, "snippet": excerpt, "source_sha256": self.sha256,
            "authority": "NONE", "execution": "NOT_AUTHORIZED"
        } for title, excerpt in rows)


def load_corpus(path: Path, expected_sha256: str) -> LanguageIndex:
    """Fail closed on tampering, invalid UTF-8 or oversized source."""
    if (not isinstance(path, Path) or path.is_symlink()
            or not isinstance(expected_sha256, str)
            or not re.fullmatch("[0-9a-f]{64}", expected_sha256)):
        raise Blocked("Fonte linguística não confiável.")
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise Blocked("Fonte linguística indisponível.") from error
    if len(raw) > 8_000_000 or hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise Blocked("A fonte linguística não corresponde à versão autorizada.")
    try:
        markdown = raw.decode("utf-8")
    except UnicodeError as error:
        raise Blocked("Fonte linguística sem UTF-8 válido.") from error
    if markdown.count("<!-- nexus-pt-PT-v1 -->") != 1:
        raise Blocked("Versão do cofre linguístico incompatível.")
    return LanguageIndex(markdown, expected_sha256)
