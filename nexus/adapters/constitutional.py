"""Reuse the pinned Conductor Markdown reader; enforce Nexus data contracts."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from conductor.config.instructions import _parse_frontmatter, _FRONTMATTER_RE
from nexus.contracts import Blocked, validate


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
    data = _parse_frontmatter(path)
    validate("multimedia", data)
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        raise Blocked("Metadados nativos ausentes.")
    return {"nome_ficheiro": path.name, "dados_yaml": data,
            "notas_markdown": text[match.end():]}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(read_object(sys.argv[1]), ensure_ascii=False))
