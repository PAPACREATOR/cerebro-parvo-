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
                    "SELECT title, snippet(pt_passages,1,'','', '...',32) FROM pt_passages "
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



def _git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def _bounded_edit_distance(a: str, b: str, max_dist: int) -> int:
    """Capped Levenshtein; determinism and speed, not execution authority."""
    if abs(len(a) - len(b)) > max_dist:
        return max_dist + 1
    prior = list(range(len(b) + 1))
    for i, ch in enumerate(a, 1):
        curr = [i]
        for j, other in enumerate(b, 1):
            curr.append(min(curr[-1] + 1, prior[j] + 1,
                            prior[j - 1] + (ch != other)))
        if min(curr) > max_dist:
            return max_dist + 1
        prior = curr
    return prior[-1]


class GeneralVocabulary:
    """Imported Portuguese data, separate from registered operational verbs."""

    def __init__(self, root: Path, manifest_sha1: str):
        if (not isinstance(root, Path) or root.is_symlink()
                or not re.fullmatch(r"[0-9a-f]{40}", manifest_sha1)):
            raise Blocked("Índice lexical geral não autorizado.")
        try:
            raw = (root / "pt_PT_MANIFESTO.md").read_bytes()
        except OSError as error:
            raise Blocked("Manifesto linguístico indisponível.") from error
        if _git_blob_sha1(raw) != manifest_sha1:
            raise Blocked("Manifesto linguístico foi alterado.")
        try:
            manifest = raw.decode("utf-8")
        except UnicodeError as error:
            raise Blocked("Manifesto linguístico não é UTF-8.") from error
        table = _section(manifest, "## Ficheiros importados\n",
                         "\nA entrada geral nunca")
        declared = {}
        for filename, blob, count in _table(table, columns=3):
            if filename == "ficheiro":
                continue
            if (filename in declared or not re.fullmatch(
                    r"pt_PT_dic_part_0[1-8]\.md|pt_PT_afixos\.md|pt_PT_LICENCA\.md",
                    filename)
                    or not re.fullmatch("[0-9a-f]{40}", blob)
                    or not re.fullmatch("[0-9]{1,5}", count)):
                raise Blocked("Referência lexical inválida.")
            declared[filename] = (blob, int(count))
        needed = {f"pt_PT_dic_part_{i:02d}.md" for i in range(1, 9)}
        needed.update(("pt_PT_afixos.md", "pt_PT_LICENCA.md"))
        if set(declared) != needed:
            raise Blocked("Importação portuguesa incompleta.")

        forms = set()
        total = 0
        for filename in sorted(needed):
            path = root / filename
            if path.is_symlink():
                raise Blocked("Fonte lexical não autorizada.")
            try:
                data = path.read_bytes()
            except OSError as error:
                raise Blocked("Parte do dicionário indisponível.") from error
            if _git_blob_sha1(data) != declared[filename][0]:
                raise Blocked("Parte do dicionário adulterada.")
            if not filename.startswith("pt_PT_dic_part_"):
                continue
            try:
                md = data.decode("utf-8")
            except UnicodeError as error:
                raise Blocked("Parte lexical não está em UTF-8.") from error
            fence = chr(96) * 3
            block = _section(md, fence + "hunspell-dic\n", "\n" + fence)
            records = block.strip("\n").splitlines()
            if len(records) != declared[filename][1]:
                raise Blocked("Dicionário português truncado.")
            total += len(records)
            for entry in records:
                head = entry.split("\t", 1)[0].split("/", 1)[0].casefold()
                if WORD.fullmatch(head):
                    forms.add(head)
        if total != 44_187 or len(forms) < 30_000:
            raise Blocked("Dicionário português incompleto.")
        self.source_blob = manifest_sha1
        self.imported_entries = total
        self.word_count = len(forms)
        self.words = frozenset(forms)
        self.by_length = {}
        for word in sorted(forms):
            self.by_length.setdefault(len(word), []).append(word)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        try:
            self.db.execute(
                "CREATE VIRTUAL TABLE pt_general USING fts5("
                "word, tokenize='unicode61 remove_diacritics 0')"
            )
            self.db.executemany(
                "INSERT INTO pt_general(word) VALUES (?)",
                ((w,) for w in sorted(forms))
            )
        except sqlite3.Error as error:
            self.db.close()
            raise Blocked("FTS5 do dicionário indisponível.") from error

    def contains(self, word: str) -> bool:
        if type(word) is not str or not WORD.fullmatch(word.casefold()):
            return False
        term = word.casefold()
        try:
            with self.lock:
                row = self.db.execute(
                    "SELECT 1 FROM pt_general WHERE word MATCH ? AND word = ? LIMIT 1",
                    ('"' + term + '"', term),
                ).fetchone()
        except sqlite3.Error as error:
            raise Blocked("Consulta ao dicionário indisponível.") from error
        return row is not None

    def fuzzy(self, word: str, limit: int = 5) -> tuple[dict, ...]:
        """Fuzzy membership 0..1, bounded, deterministic and advisory only."""
        if type(word) is not str or type(limit) is not int or not 1 <= limit <= 10:
            raise Blocked("Consulta fuzzy inválida.")
        term = word.casefold()
        if not WORD.fullmatch(term) or len(term) < 3 or self.contains(term):
            return ()
        threshold = 1 if len(term) <= 4 else 2
        sizes = range(max(1, len(term) - threshold), len(term) + threshold + 1)
        candidates = (candidate for size in sizes
                      for candidate in self.by_length.get(size, ())
                      if candidate[0] == term[0])
        matches = []
        for candidate in candidates:
            distance = _bounded_edit_distance(term, candidate, threshold)
            if distance <= threshold:
                membership = round(1 - distance / max(len(term), len(candidate)), 4)
                matches.append((membership, distance, candidate))
        matches.sort(key=lambda item: (-item[0], item[1], item[2]))
        return tuple({
            "candidate": candidate, "membership": membership,
            "edit_distance": distance, "source": "pt-PT-Hunspell-Markdown",
            "source_blob": self.source_blob,
            "status": "SUGGESTION", "authority": "NONE",
            "execution": "NOT_AUTHORIZED",
        } for membership, distance, candidate in matches[:limit])


def load_general_vocabulary(root: Path, manifest_sha1: str) -> GeneralVocabulary:
    return GeneralVocabulary(root, manifest_sha1)
