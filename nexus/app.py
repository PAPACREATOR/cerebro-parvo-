"""Loopback-only Folha Nexus server using the Python standard library."""
import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import socket
import sqlite3
import sys
import threading
import time
import unicodedata
import webbrowser
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from nexus.contracts import ROOT, Blocked, strict_json, validate
from nexus.frontdoor import parse, propose_operation
from nexus.capability_router import declared_router, registered_router
from nexus.adapters.constitutional import build_molde
from nexus.host import Host
from nexus.instance import data_directory_lock
from nexus.store import atomic


_PREEXECUTION_TTL_SECONDS = 180
_MAX_PREEXECUTION_TICKETS = 64

# Laboratory code is not in Host.verify_integrity()'s fixed required set.
# Pin its exact audited bytes here: app.py itself is Host-sealed. Never import
# mutable experimental code into the product without verifying these digests.
_PINNED_WIKI_LAB = {
    "lab/wiki/kernel_bridge.py": "d9560b680b1b783acca3aec4effc1142d95944f14c7d26c5f1d8511c9d71a2ef",
    "lab/wiki/context_packet.py": "b82b1c7899a6f088e51cfd90aab3554a2bbace9f4f123fab20283e95362ef6e8",
}


def _verified_wiki_bridge(store):
    for relative, expected in _PINNED_WIKI_LAB.items():
        target = ROOT / relative
        if target.is_symlink() or target.is_junction() or not target.is_file():
            raise Blocked("Componente de pesquisa não autorizado.")
        if not secrets.compare_digest(hashlib.sha256(target.read_bytes()).hexdigest(), expected):
            raise Blocked("A integridade do módulo FTS5 mudou; pesquisa bloqueada.")
    # Reuse the original laboratory's Store verification and FTS5 implementation.
    from nexus.lab.wiki.kernel_bridge import WikiBridge

    # Derived SQLite index must be outside the sovereign Store and Git tree.
    index_root = store.root.parent / (store.root.name + "-fts5-index")
    if index_root.is_symlink() or index_root.is_junction():
        raise Blocked("Índice de pesquisa redirecionado.")
    return WikiBridge(store, index_root)


_PINNED_GRAPH_SHA256 = "ac9a972c5a3b066285c6eb2a478c15a4d32eddec123af29e21ba1b41e5bfeb33"


def _verified_graph(store):
    # The graph is a derived index, not an authority. Pin its audited source.
    module = ROOT / "graph" / "graph_minimo.py"
    if (module.is_symlink() or module.is_junction() or not module.is_file()
            or not secrets.compare_digest(hashlib.sha256(module.read_bytes()).hexdigest(),
                                          _PINNED_GRAPH_SHA256)):
        raise Blocked("Integridade do grafo alterada; pesquisa bloqueada.")
    from nexus.graph.graph_minimo import GraphMinimo

    root = store.root.parent / (store.root.name + "-fts5-index")
    file = root / "graph.sqlite"
    if root.is_symlink() or root.is_junction() or file.is_symlink() or file.is_junction():
        raise Blocked("Índice de relações redirecionado.")
    return GraphMinimo(file)


def _request_digest(request):
    raw = json.dumps(
        request, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _natural_work_process(text):
    """Deterministic process proposal for bounded natural text, never authority."""
    if not isinstance(text, str) or not text.strip() or len(text) > 12000:
        return None
    from nexus.frontdoor import requires_clarification
    if requires_clarification(text):
        return None
    normal = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).casefold()).strip()
    if re.search(r"\b(?:apaga|elimina|remove|desativa|envia|publica|instala|executa|transfere)\b", normal):
        return None
    web = re.match(
        r"^(?:por favor[, ]+)?(?:pesquisa|pesquisar|procura|procurar|encontra|encontrar)"
        r"\s+(?:(?:na\s+)?(?:web|internet)\s+)?(?:(?:fontes?|informações)\s+)?"
        r"(?:(?:sobre|acerca de|para)\s+)?(.+)$", normal,
    )
    if web:
        subject = web.group(1).strip(" .?!")
        if subject and subject not in {"web", "internet", "na web", "na internet", "fontes"}:
            return "web"
    candidate = re.match(
        r"^(?:por favor[, ]+)?(?:cria|criar|faz|fazer|prepara|preparar|"
        r"quero\s+(?:criar|fazer|preparar)|preciso\s+de)\s+"
        r"(?:(?:um|uma|o|a)\s+)?"
        r"(podcast\s+visual|podcast|v[ií]deo|curta(?:-metragem)?|m[uú]sica|can[cç][aã]o)\b",
        normal,
    )
    if not candidate:
        return None
    family = candidate.group(1)
    if family == "podcast visual":
        return "visual_podcast"
    if family == "podcast":
        return "podcast"
    if family in ("vídeo", "video", "curta", "curta-metragem"):
        return "video"
    return "music"


def _natural_assistant(text):
    """Read-only conversational preparation by Nexus; tools have no say here."""
    process = _natural_work_process(text)
    if process not in {"podcast", "visual_podcast", "video", "music"}:
        return {"process": process, "question": None, "missing": []}
    normal = unicodedata.normalize("NFKC", text).casefold()
    # Fixed recognition, not an invented default. Unsupported tone words can
    # be supplied explicitly as 'tom: ...' or 'estilo: ...'.
    tone = bool(re.search(
        r"\b(?:documental|jornalístico|jornalistico|informal|formal|académico|academico|"
        r"narrativo|educativo|didático|didatico|descontraído|descontraido|"
        r"humorístico|humoristico|humor|sério|serio|emocional|conversacional|"
        r"cinematográfico|cinematografico|folk|fado|rock|rap|pop|clássico|classico)\b",
        normal,
    ) or re.search(r"\b(?:tom|estilo)\s*:\s*\S+", normal))
    duration = bool(re.search(
        r"\b\d+(?:[.,]\d+)?\s*(?:segundos?|seg|minutos?|min|horas?|h)\b",
        normal,
    ))
    missing = []
    if not tone:
        missing.append("tom")
    if not duration:
        missing.append("duração")
    questions = {
        ("tom", "duração"): "Que tom pretendes e quanto deve durar?",
        ("tom",): "Que tom pretendes?",
        ("duração",): "Quanto deve durar?",
    }
    return {"process": process, "question": questions.get(tuple(missing)), "missing": missing}


def _natural_request(data, host):
    """Build one bounded request proposal. This function never executes it."""
    if not isinstance(data, dict) or set(data) != {"text", "filename", "attachment"}:
        raise Blocked("Pedido natural inválido.")
    if not all(isinstance(data[key], str) for key in data):
        raise Blocked("Pedido natural inválido.")

    parsed = parse(data["text"])
    process = propose_operation(
        parsed, filename=data["filename"], attachment=data["attachment"]
    )
    if process is None and parsed.status == "RESOLVED":
        # Match the whole registered command after the intent is resolved.
        # A proposal never grants permission to execute the selected function.
        candidate = registered_router().propose(
            intent=parsed.intent, text=parsed.content,
            attachment_present=bool(data["filename"] and data["attachment"]),
        )
        process = candidate.process
    inferred = _natural_work_process(data["text"]) if not data["filename"] and not data["attachment"] else None
    if process is None and parsed.status != "BLOCKED":
        process = inferred
    if process is None:
        raise Blocked("Não consigo determinar com segurança essa operação. Reformula o pedido.")

    if process == "verify":
        # The legacy operation rule finds a verification inside larger text.
        # A human ticket must cover one complete request, never that substring.
        command = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", parsed.content).casefold()).strip()
        if not re.fullmatch(
            r"(?:por favor,? )?(?:podes )?verific(?:a|ar|as|ares) (?:a )?integridade "
            r"(?:(?:de um|deste|desse|do|dum|de) )?(?:ficheiro|documento|arquivo)[.!?]?",
            command,
        ):
            raise Blocked("Pede uma única verificação do ficheiro. Separa outras ações num novo pedido.")

    request = {"process": process, **data}
    validate("request", request)
    try:
        attachment = base64.b64decode(request["attachment"], validate=True)
    except (ValueError, TypeError) as error:
        raise Blocked("Anexo inválido.") from error
    text_only = inferred == process and not request["filename"] and not request["attachment"]
    if text_only:
        attachment = request["text"].encode("utf-8")
    if not attachment or len(attachment) > host.store.policy["max_input_bytes"]:
        raise Blocked("O pedido ou o ficheiro ultrapassa o limite permitido.")
    name = request["filename"] if not text_only else "pedido"
    if not name or any(ord(char) < 32 for char in name) or "/" in name or "\\" in name:
        raise Blocked("Nome de anexo inválido.")

    if process in ("convert_pdf", "book"):
        # A conversion proposal may never interpret arbitrary file bytes,
        # scripts, macros, external objects, or an extension/MIME mismatch.
        from nexus.adapters.office import document_kind
        ext = Path(name).suffix.lower()
        if ext not in (".odt", ".docx"):
            raise Blocked("A exportação requer um documento DOCX ou ODT válido e com extensão correspondente.")
        try:
            kind = document_kind(attachment)
        except Blocked:
            raise
        except Exception as error:
            # Untrusted ZIP decoding can raise NotImplementedError for an
            # unsupported compression method (and other decoder failures).
            # No parser exception may escape the HTTP refusal boundary.
            raise Blocked("O documento não pode ser validado em segurança.") from error
        if kind != ext:
            raise Blocked("A extensão não corresponde ao conteúdo DOCX ou ODT.")
    descriptions = {
        "verify": "Verificar a integridade de " + name + ".",
        "interpret": "Pedir interpretação da fonte " + name + " à bancada OpenNotebook configurada.",
        "proofread": "Rever " + name + " com LanguageTool local configurado.",
        "convert_pdf": "Converter " + name + " para PDF; original conservado. Não altera os estilos.",
        "video": "Preparar plano de vídeo a partir de " + name + "; não renderiza vídeo.",
        "podcast": "Preparar plano de podcast a partir de " + name + "; não gera áudio.",
        "visual_podcast": "Preparar plano de podcast visual a partir de " + name + "; não gera vídeo.",
        "book": "Exportar o manuscrito " + name + " para PDF; não cria nem redesenha o livro.",
        "music": "Preparar plano de música a partir de " + name + "; não gera áudio.",
        "web": "Preparar plano de pesquisa web a partir de " + name + "; não navega automaticamente.",
    }
    return request, {
        "molde": build_molde(data["text"], data["filename"], data["attachment"],
                              intent=parsed.intent, process=process),
        "process": process,
        "filename": name,
        "attachment_bytes": len(attachment),
        "attachment_sha256": hashlib.sha256(attachment).hexdigest(),
        "summary": descriptions[process],
        "parser": parsed.parser,
    }


class NexusHTTPServer(ThreadingHTTPServer):
    # Windows SO_REUSEADDR permits two listeners on the same address/port.
    allow_reuse_address = os.name != "nt"

    def server_bind(self):
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def make_server(host, port=0, *, allow_direct_run=False):
    preexecution_tickets = {}
    preexecution_lock = threading.Lock()
    memory_lock = threading.Lock()
    memory_state = {"bridge": None, "revision": None, "graph_revision": None}

    def search_memory(data, session):
        # Exact schema, no tool execution, no approval or Store mutation.
        if not isinstance(data, dict) or set(data) != {"query", "include_creative", "limit"}:
            raise Blocked("Consulta de memória inválida.")
        query, creative, limit = data["query"], data["include_creative"], data["limit"]
        if (not isinstance(query, str) or not query.strip() or len(query) > 200 or
                "\x00" in query or type(creative) is not bool or type(limit) is not int or
                not 1 <= limit <= 8):
            raise Blocked("Consulta de memória inválida.")
        # Authorization and visible state come from the authoritative Host.
        visible = host.list_runs(session)
        allowed = [item["run_id"] for item in visible
                   if item["status"] == "PASS" or
                   (creative and item["status"] == "HUMAN_REQUIRED")]
        scope = "canonical+creative" if creative else "canonical"
        if not allowed:
            return {"scope": scope, "results": []}
        revision = tuple(sorted((item["run_id"], item["status"], item.get("updated_at"),
                                 item.get("candidate_sha256"), item.get("provenance_sha256"))
                                for item in visible))
        with memory_lock:
            try:
                # Recheck all imported laboratory bytes at every query.
                checked = _verified_wiki_bridge(host.store)
                bridge = memory_state["bridge"]
                if bridge is None:
                    bridge = checked
                    memory_state["bridge"] = bridge
                if memory_state["revision"] != revision or not bridge.index.is_file():
                    bridge.rebuild()  # atomic derived rebuild; originals untouched.
                    memory_state["revision"] = revision
                found = bridge.search(query, allowed, include_creative=creative, limit=limit)
                # Store-verified snapshots only; graph cannot promote vault data.
                graph = _verified_graph(host.store)
                graph_revision = (scope, revision)
                snapshots = [bridge.snapshot(run_id, include_creative=creative)
                             for run_id in allowed]
                if memory_state["graph_revision"] != graph_revision or not graph.db_path.is_file():
                    graph.reconstruir_snapshots(snapshots)
                    memory_state["graph_revision"] = graph_revision
                by_run = {item["run_id"]: item for item in snapshots}
                visible_ids = set(by_run)
                related = {}
                for item in found:
                    linked = []
                    for run_id in graph.relacionados(item["run_id"], visible_ids):
                        other = by_run[run_id]
                        # Authentic hashes, never graph labels, decide provenance.
                        if other["input_sha256"] != item["input_sha256"]:
                            raise Blocked("Índice do grafo inconsistente com a fonte.")
                        linked.append({
                            "authority": other["authority"],
                            "process_id": other["process_id"],
                            "snippet": other["content"][:240],
                        })
                    related[item["run_id"]] = linked
            except (OSError, sqlite3.Error) as error:
                raise Blocked("Índice de memória indisponível; conteúdo original preservado.") from error
        return {"scope": scope, "results": [
            {"run_id": item["run_id"], "authority": item["authority"],
             "process_id": item["process_id"], "snippet": item["content"][:240],
             "content_sha256": item["content_sha256"],
             "provenance_sha256": item["provenance_sha256"],
             "related": related[item["run_id"]]}
            for item in found]}

    def verified_molde(run_id, state):
        """Read-only projection of the exact Store-verified source and execution."""
        host.store.check_input(state)
        request = validate("request", strict_json(
            host.store.checked_bytes("runs", run_id, "request.json")))
        parsed = parse(request["text"])
        mold = build_molde(request["text"], request["filename"], request["attachment"],
                           intent=parsed.intent if parsed.status == "RESOLVED" else None,
                           process=request["process"])
        if not secrets.compare_digest(mold["source"]["sha256"], state["input_sha256"]):
            raise Blocked("O molde não corresponde ao original verificado.")
        mold["record"] = {
            "run_id": run_id,
            "created_at": state["created_at"],
            "status": state["status"],
            "process_version": state["process_version"],
        }
        return mold

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, code, payload, content_type="application/json; charset=utf-8"):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if not isinstance(payload, bytes) else payload
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(body)

        def guard(self):
            address = "127.0.0.1:" + str(self.server.server_port)
            if self.headers.get("Host") != address:
                raise Blocked("Origem inválida.")
            origin = self.headers.get("Origin")
            if origin and origin != "http://" + address:
                raise Blocked("Origem inválida.")
            return self.headers.get("X-Nexus-Session", "")

        def do_GET(self):
            try:
                session = self.guard()
                path = urlsplit(self.path).path
                assets = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"), "/style.css": ("style.css", "text/css")}
                if path in assets:
                    filename, mime = assets[path]
                    return self.reply(200, (ROOT / "ui" / filename).read_bytes(), mime + "; charset=utf-8")
                host.authorize(session)
                if path == "/api/runs":
                    return self.reply(200, host.list_runs(session))
                if path.startswith("/api/pdf/"):
                    return self.reply(200, host.artifact(path.split("/")[-1], session), "application/pdf")
                if path.startswith("/api/runs/"):
                    run_id = path.split("/")[-1]
                    detail = host.detail(run_id, session)
                    detail["molde"] = verified_molde(run_id, detail)
                    return self.reply(200, detail)
                self.reply(404, {"error": "Não encontrado."})
            except (Blocked, FileNotFoundError) as error:
                self.reply(403, {"error": str(error)})

        def do_POST(self):
            try:
                session = self.guard()
                host.authorize(session)
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 3_200_000 or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                    raise Blocked("Pedido inválido ou demasiado grande.")
                data = strict_json(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise Blocked("Pedido inválido.")
                path = urlsplit(self.path).path
                if path == "/api/search":
                    return self.reply(200, search_memory(data, session))
                if path == "/api/interpret":
                    # Read-only Folha interpretation. Parsing never executes,
                    # creates Store records, or grants any tool permission.
                    if set(data) != {"text"} or not isinstance(data["text"], str):
                        raise Blocked("Pedido de interpretação inválido.")
                    parsed = parse(data["text"])
                    command = (declared_router().recognise_command(parsed.content)
                               if parsed.status == "RESOLVED" else None)
                    return self.reply(200, {
                        "status": parsed.status,
                        "intent": parsed.intent,
                        "original": parsed.original,
                        "parser": parsed.parser,
                        "confirmation_required": False,
                        "execution": "NOT_AUTHORIZED",
                        "registered_command": command is not None and command.intent == parsed.intent,
                        "assistant": _natural_assistant(data["text"]) if parsed.status != "BLOCKED" else {"process": None, "question": None, "missing": []},
                        "molde": build_molde(data["text"], intent=parsed.intent if parsed.status == "RESOLVED" else None)
                                 if data["text"] else None,
                    })
                if path == "/api/prepare-run":
                    request, preview = _natural_request(data, host)
                    now = time.monotonic()
                    with preexecution_lock:
                        expired = [
                            key for key, value in preexecution_tickets.items()
                            if value["expires"] <= now
                        ]
                        for key in expired:
                            preexecution_tickets.pop(key, None)
                        if len(preexecution_tickets) >= _MAX_PREEXECUTION_TICKETS:
                            raise Blocked("Há demasiados pedidos pendentes de confirmação.")
                        ticket = secrets.token_urlsafe(32)
                        preexecution_tickets[ticket] = {
                            "request_sha256": _request_digest(request),
                            "expires": now + _PREEXECUTION_TTL_SECONDS,
                        }
                    return self.reply(200, {"ticket": ticket, **preview})
                if path == "/api/confirm-run":
                    if set(data) != {"ticket", "confirmed", "text", "filename", "attachment"}:
                        raise Blocked("Confirmação de execução inválida.")
                    ticket = data["ticket"]
                    if not isinstance(ticket, str):
                        raise Blocked("Confirmação de execução inválida.")
                    with preexecution_lock:
                        binding = preexecution_tickets.pop(ticket, None)
                    if not binding or binding["expires"] <= time.monotonic():
                        raise Blocked("A confirmação expirou ou já foi usada.")
                    if data["confirmed"] is False:
                        return self.reply(200, {"status": "CANCELLED"})
                    if data["confirmed"] is not True:
                        raise Blocked("É necessária confirmação humana explícita.")
                    current = {
                        "text": data["text"],
                        "filename": data["filename"],
                        "attachment": data["attachment"],
                    }
                    request, _preview = _natural_request(current, host)
                    if not secrets.compare_digest(
                        binding["request_sha256"], _request_digest(request)
                    ):
                        raise Blocked("O pedido mudou depois da revisão. Confirma novamente.")
                    return self.reply(202, host.start(request, session))
                if path == "/api/run":
                    # Diagnostic/test route only. The product server never enables it.
                    if not allow_direct_run:
                        raise Blocked("A execução direta requer modo de diagnóstico explícito.")
                    return self.reply(202, host.start(data, session))
                if path == "/api/prepare" and set(data) == {"run_id"}:
                    return self.reply(200, host.prepare_approval(data["run_id"], session))
                if path == "/api/approve" and set(data) == {"run_id", "ticket", "confirmed"}:
                    return self.reply(200, host.approve(data["run_id"], data["ticket"], data["confirmed"], session))
                raise Blocked("Operação não autorizada.")
            except (Blocked, ValueError, KeyError, FileNotFoundError) as error:
                self.reply(403, {"error": str(error)})

    return NexusHTTPServer(("127.0.0.1", port), Handler)


@contextmanager
def application(data_root, port=0):
    # Acquire ownership before Store's startup reconciliation can write anything.
    with data_directory_lock(data_root) as root:
        host = Host(root)
        server = make_server(host, port)
        try:
            yield host, server
        finally:
            try:
                server.server_close()
            finally:
                # Normal shutdown must not release ownership while _run writes.
                with host.busy:
                    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "runtime")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    try:
        with application(args.data, args.port) as (host, server):
            url = "http://127.0.0.1:" + str(server.server_port) + "/#session=" + host.session
            # Private local launch reference; ignored by Git, never given to tools.
            atomic(host.store.root / "launch-url.txt", url.encode("utf-8"))
            print("Folha Nexus pronta. Mantém esta janela aberta.", flush=True)
            if not args.no_browser:
                webbrowser.open(url)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    except Blocked as error:
        print("Nexus: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
