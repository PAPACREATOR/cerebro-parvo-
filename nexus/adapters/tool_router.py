"""Fail-closed capability proposals; never executes tools or grants authority.

Only Host.start, behind the independent one-use human HTTP confirmation,
may enter Store/Kernel and run the fixed native/Sandy adapters.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from nexus.contracts import Blocked, load_policy, validate
from nexus.frontdoor import parse, propose_operation
from nexus.adapters.runner import PROCESS_TO_TOOL, PROCESS_FILES


@dataclass(frozen=True, slots=True)
class ToolAdapter:
    """One policy-bound capability with an identical pre-execution interface."""

    process: str
    tool: str
    title: str
    preflight: Callable[[bytes, str], None]

    def inspect(self, raw: bytes, filename: str) -> str:
        self.preflight(raw, filename)
        subject = filename or "texto escrito"
        return self.title + " — " + subject + ". O original será preservado."


def _binary(raw: bytes, _filename: str) -> None:
    if not raw:
        raise Blocked("Ficheiro vazio.")


def _text(raw: bytes, _filename: str) -> None:
    from nexus.adapters.product_routes import prepare_text
    prepare_text(raw)


def _notebook(raw: bytes, _filename: str) -> None:
    from nexus.adapters.notebook import prepare_source
    prepare_source(raw)


def _music(raw: bytes, filename: str) -> None:
    _text(raw, filename)
    from nexus.adapters.product_routes import _sections
    _sections(raw.decode("utf-8"))


def _writer(raw: bytes, filename: str) -> None:
    from nexus.adapters.office import document_kind
    suffix = Path(filename).suffix.lower()
    if suffix not in (".odt", ".docx"):
        raise Blocked("A exportação Writer exige DOCX/ODT válido e extensão correspondente.")
    try:
        kind = document_kind(raw)
    except Blocked:
        raise
    except Exception as error:
        # Untrusted ZIP methods/decoders must never become an HTTP 500.
        raise Blocked("O documento não pode ser validado em segurança.") from error
    if kind != suffix:
        raise Blocked("A extensão não corresponde ao documento DOCX/ODT.")


# Adding a new adapter alone NEVER extends Store policy or the executable
# Host: human-reviewed policy, schema, pinned files and sandbox are prerequisites.
_SPECS: tuple[tuple[str, str, Callable[[bytes, str], None]], ...] = (
    ("verify", "Verificar integridade", _binary),
    ("interpret", "Interpretar texto com OpenNotebook local", _notebook),
    ("proofread", "Rever texto com LanguageTool local", _text),
    ("convert_pdf", "Converter para PDF com Writer", _writer),
    ("video", "Preparar plano de vídeo com OpenNotebook", _text),
    ("podcast", "Preparar plano de podcast com OpenNotebook", _text),
    ("visual_podcast", "Preparar plano de podcast visual com OpenNotebook", _text),
    ("book", "Exportar manuscrito para PDF com Writer", _writer),
    ("music", "Preparar especificação musical (não gera áudio)", _music),
    ("web", "Preparar consulta web (não pesquisa a Internet)", _text),
)


def available_adapters() -> dict[str, ToolAdapter]:
    """Construct an N-entry registry, pinned to already permitted Host routes."""
    allowed = set(load_policy()["processes"])
    if allowed != set(PROCESS_TO_TOOL) or allowed != set(PROCESS_FILES):
        raise Blocked("Contratos de capacidade não coincidem.")
    if len(_SPECS) != len(allowed) or {row[0] for row in _SPECS} != allowed:
        raise Blocked("Registo de ferramentas incompleto ou duplicado.")
    return {
        process: ToolAdapter(process, PROCESS_TO_TOOL[process], title, check)
        for process, title, check in _SPECS
    }


def route_request(data: object, *, max_input_bytes: int) -> tuple[dict, dict]:
    """Pure proposal → exact adapter → bounded source + preview; NO execution."""
    if not isinstance(data, dict) or set(data) != {"text", "filename", "attachment"}:
        raise Blocked("Pedido natural inválido.")
    if not all(type(data[k]) is str for k in data):
        raise Blocked("Pedido natural inválido.")
    parsed = parse(data["text"])
    process = propose_operation(
        parsed, filename=data["filename"], attachment=data["attachment"]
    )
    adapters = available_adapters()
    if process not in adapters:
        raise Blocked("Não existe uma ferramenta única autorizada para esse pedido.")
    filename = data["filename"]
    if any(ord(c) < 32 for c in filename) or any(c in '/\\:' for c in filename):
        raise Blocked("Nome de anexo inválido.")
    if (filename and not data["attachment"]) or (data["attachment"] and not filename):
        raise Blocked("Anexo e nome devem estar presentes em conjunto.")
    request = {"process": process, **data}
    validate("request", request)
    if data["attachment"]:
        try:
            raw = base64.b64decode(data["attachment"], validate=True)
        except (ValueError, TypeError) as error:
            raise Blocked("Anexo inválido.") from error
    else:
        raw = data["text"].encode("utf-8")
    if not raw or len(raw) > max_input_bytes:
        raise Blocked("Ficheiro ou texto fora do limite de 2 MB.")
    adapter = adapters[process]
    description = adapter.inspect(raw, filename)
    import hashlib
    return request, {
        "process": process,
        "filename": filename or "Texto escrito",
        "attachment_bytes": len(raw),
        "attachment_sha256": hashlib.sha256(raw).hexdigest(),
        "summary": description,
        "parser": parsed.parser,
    }
