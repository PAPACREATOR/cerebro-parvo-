"""Strict Markdown object reader owned by Nexus; no external workflow parser."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nexus.contracts import Blocked, strict_json, validate

KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,63}$")
VALUE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


def _frontmatter(text):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].lstrip("\ufeff").strip() != "---":
        raise Blocked("Metadados nativos ausentes.")
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        raise Blocked("Metadados nativos incompletos.")
    body = "".join(lines[1:end]).strip()
    if not body:
        raise Blocked("Metadados nativos vazios.")
    if body.startswith("{"):
        data = strict_json(body)
    else:
        data = {}
        for raw in body.splitlines():
            line = raw.strip()
            if not line or ":" not in line or line.startswith(("!", "&", "*", "{", "[", "-")):
                raise Blocked("Frontmatter fora do subconjunto seguro.")
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if not KEY.fullmatch(key) or not VALUE.fullmatch(value) or key in data:
                raise Blocked("Frontmatter fora do subconjunto seguro.")
            data[key] = value
    if not isinstance(data, dict):
        raise Blocked("Frontmatter precisa de ser um objeto.")
    offset = sum(len(item) for item in lines[: end + 1])
    return data, text[offset:]


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
    data, notes = _frontmatter(text)
    validate("multimedia", data)
    return {"nome_ficheiro": path.name, "dados_yaml": data, "notas_markdown": notes}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(read_object(sys.argv[1]), ensure_ascii=False))


def build_molde(text, filename="", attachment="", *, intent=None, process=None):
    """Read-only, non-authoritative envelope for any Folha input.

    It classifies *hints*, never facts: file suffixes are not trusted MIME
    evidence, an intent is not execution, and this object is not Store state.
    The only content identity is the SHA-256 of the exact original bytes.
    """
    import base64
    import binascii
    import hashlib

    if any(type(value) is not str for value in (text, filename, attachment)):
        raise Blocked("Entrada do molde inválida.")
    if len(text) > 100_000 or len(filename) > 200 or len(attachment) > 2_796_204:
        raise Blocked("Entrada do molde demasiado grande.")
    if any(ord(char) < 32 or ord(char) == 127 or char in "/\\" for char in filename):
        raise Blocked("Nome de ficheiro do molde inválido.")
    try:
        text.encode("utf-8")
        filename.encode("utf-8")
    except UnicodeError as error:
        raise Blocked("Texto ou nome com Unicode inválido.") from error
    if intent is not None and (type(intent) is not str or len(intent) > 100):
        raise Blocked("Intenção do molde inválida.")
    if process is not None and (type(process) is not str or len(process) > 100):
        raise Blocked("Processo do molde inválido.")
    if attachment:
        if not filename:
            raise Blocked("Anexo sem nome de ficheiro.")
        try:
            raw = base64.b64decode(attachment, validate=True)
        except (ValueError, binascii.Error) as error:
            raise Blocked("Anexo do molde inválido.") from error
        kind = "file"
    else:
        if filename:
            raise Blocked("Nome de ficheiro sem anexo.")
        raw = text.encode("utf-8")
        kind = "text"
    if not raw or len(raw) > 2_097_152:
        raise Blocked("Conteúdo do molde fora do limite.")

    # File extensions are untrusted descriptive hints, not verified media types.
    extension = Path(filename).suffix.lower() if filename else ""
    hints = {
        ".txt": "document", ".md": "document", ".pdf": "document",
        ".odt": "document", ".docx": "document", ".ott": "document",
        ".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image",
        ".wav": "audio", ".mp3": "audio", ".flac": "audio",
        ".mp4": "video", ".mkv": "video", ".mov": "video",
    }
    digest = hashlib.sha256(raw).hexdigest()
    return {
        "schema": "nexus.molde.v1",
        "identity": {"id": "sha256:" + digest, "version": 1},
        "source": {"channel": "folha", "kind": kind, "filename": filename or None,
                   "bytes": len(raw), "sha256": digest},
        "classification": {
            "type": kind,
            "family": "text" if kind == "text" else hints.get(extension, "unknown"),
            "basis": "original_bytes" if kind == "text" else "untrusted_filename_hint",
            "intent": intent,
        },
        "process": {"candidate": process, "authority": "NONE"},
        "relations": [],
        "record": None,
        "rules": {"execution": "HUMAN_CONFIRMATION",
                  "promotion": "HUMAN_APPROVAL",
                  "deletion": "NOT_AUTHORIZED"},
    }
