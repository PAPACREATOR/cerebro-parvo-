"""Bounded document conversion through installed LibreOffice; no AI."""
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nexus.windows_sandbox import require_native_boundary
from nexus.contracts import Blocked, strict_json


def document_kind(raw):
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = archive.infolist()
            if len(entries) > 2000 or sum(e.file_size for e in entries) > 20_000_000:
                raise Blocked("Documento demasiado complexo para este ensaio.")
            names = {e.filename for e in entries}
            if len(names) != len(entries):
                raise Blocked("Documento com entradas repetidas.")
            for entry in entries:
                name = entry.filename.lower()
                if any(word in name for word in ("vbaproject", "scripts/", "basic/", "embeddings/")):
                    raise Blocked("Conteúdo ativo não permitido neste ensaio.")
                if name.endswith((".xml", ".rels")):
                    body = archive.read(entry).lower()
                    import re
                    if any(word in body for word in (b'<!entity', b'<!doctype')) or re.search(rb'targetmode\s*=\s*[\x22\x27]external|(?:xlink:href|href)\s*=\s*[\x22\x27](?:https?:|file:)', body):
                        raise Blocked("Ligação externa não permitida neste ensaio.")
            if "word/document.xml" in names and "[Content_Types].xml" in names:
                return ".docx"
            if "mimetype" in names and archive.read("mimetype") == b"application/vnd.oasis.opendocument.text" and "content.xml" in names:
                return ".odt"
    except (zipfile.BadZipFile, RuntimeError, OSError) as error:
        raise Blocked("Anexa um documento DOCX ou ODT válido.") from error
    raise Blocked("Anexa um documento DOCX ou ODT válido.")


def pdf_bytes(path):
    if path.is_symlink() or not path.is_file() or not 20 < path.stat().st_size <= 8_000_000:
        raise Blocked("PDF ausente ou inválido.")
    raw = path.read_bytes()
    if not raw.startswith(b"%PDF-") or b"%%EOF" not in raw[-1024:]:
        raise Blocked("PDF incompleto.")
    return raw


def run(input_path):
    source = Path(input_path)
    raw = source.read_bytes()
    kind = document_kind(raw)
    config = strict_json((source.parent / "libreoffice.json").read_bytes())
    if not isinstance(config, dict) or set(config) != {"executable"} or not isinstance(config["executable"], str):
        raise Blocked("Configuração LibreOffice inválida.")
    executable = Path(config["executable"])
    if not executable.is_absolute() or not executable.is_file() or executable.name.lower() != "soffice.com":
        raise Blocked("LibreOffice indisponível.")
    if sys.platform == "win32":
        require_native_boundary()
    working = source.parent / "office"
    working.mkdir()
    document = working / ("resultado" + kind)
    document.write_bytes(raw)
    profile = working / "profile"
    profile.mkdir()
    (profile / "user").mkdir()
    (profile / "user/registrymodifications.xcu").write_text(
        '<?xml version="1.0"?><oor:items xmlns:oor="http://openoffice.org/2001/registry">'
        '<item oor:path="/org.openoffice.Office.Common/Security/Scripting"><prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop></item></oor:items>', encoding="utf-8")
    command = [str(executable), "-env:UserInstallation=" + profile.as_uri(), "--headless", "--norestore", "--convert-to", "pdf:writer_pdf_Export", "--outdir", str(source.parent), str(document)]
    with (working / "stdout.txt").open("wb") as stdout, (working / "stderr.txt").open("wb") as stderr:
        proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            code = proc.wait(timeout=45)
        except subprocess.TimeoutExpired:
            subprocess.run([str(Path(os.environ["SystemRoot"]) / "System32/taskkill.exe"), "/PID", str(proc.pid), "/T", "/F"], capture_output=True, timeout=10)
            proc.kill(); proc.wait()
            raise Blocked("Conversão excedeu o tempo permitido.") from None
    if code != 0:
        raise Blocked("LibreOffice não concluiu a conversão.")
    pdf = pdf_bytes(source.parent / "resultado.pdf")
    sha = hashlib.sha256(pdf).hexdigest()
    return {"status": "UNKNOWN", "outcome": "candidate", "title": "PDF convertido",
            "markdown": "# PDF convertido\n\nO original foi conservado. Revê o PDF antes de aprovar; a conversão não prova a fidelidade do conteúdo.",
            "ai_calls": 0, "artifact": {"name": "resultado.pdf", "sha256": sha},
            "evidence": [{"capability": "libreoffice.writer-pdf", "status": "PASS", "value": sha}]}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        print(json.dumps(run(sys.argv[1]), ensure_ascii=False))
    except Exception:
        print("Conversão indisponível ou documento rejeitado.", file=sys.stderr)
        raise SystemExit(1)
