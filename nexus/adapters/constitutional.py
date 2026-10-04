"""Read Nexus Markdown frontmatter with a local deterministic parser."""
import json
import re
import sys
from pathlib import Path

from ruamel.yaml import YAML

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nexus.contracts import Blocked, validate


_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)


def _frontmatter(text):
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        raise Blocked("Metadados nativos ausentes.")
    parser = YAML(typ="safe")
    parser.allow_duplicate_keys = False
    try:
        data = parser.load(match.group(1))
    except Exception as error:
        raise Blocked("Frontmatter inválido.") from error
    if not isinstance(data, dict):
        raise Blocked("Frontmatter inválido.")
    return data, match.end()


def read_object(path):
    path = Path(path)
    if path.suffix.lower() != ".md" or path.is_symlink():
        raise Blocked("É necessário um ficheiro Markdown regular.")
    raw = path.read_bytes()
    if len(raw) > 100_000:
        raise Blocked("Objeto demasiado grande.")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as error:
        raise Blocked("Markdown precisa de UTF-8.") from error
    data, end = _frontmatter(text)
    validate("multimedia", data)
    return {
        "nome_ficheiro": path.name,
        "dados_yaml": data,
        "notas_markdown": text[end:],
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(read_object(sys.argv[1]), ensure_ascii=False))
