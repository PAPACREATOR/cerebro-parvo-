"""Loopback-only Folha Nexus server using the Python standard library."""
import argparse
import base64
import hashlib
import json
import os
import secrets
import socket
import sys
import threading
import time
import webbrowser
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from nexus.contracts import ROOT, Blocked, strict_json, validate
from nexus.frontdoor import parse, propose_operation
from nexus.host import Host
from nexus.instance import data_directory_lock
from nexus.store import atomic


_PREEXECUTION_TTL_SECONDS = 180
_MAX_PREEXECUTION_TICKETS = 64


def _request_digest(request):
    raw = json.dumps(
        request, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


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
    if process != "verify":
        raise Blocked("Não consigo determinar com segurança essa operação. Reformula o pedido.")

    request = {"process": process, **data}
    validate("request", request)
    try:
        attachment = base64.b64decode(request["attachment"], validate=True)
    except (ValueError, TypeError) as error:
        raise Blocked("Anexo inválido.") from error
    if not attachment or len(attachment) > host.store.policy["max_input_bytes"]:
        raise Blocked("Junta um ficheiro até 2 MB para verificar.")
    name = request["filename"]
    if not name or any(ord(char) < 32 for char in name) or "/" in name or "\\" in name:
        raise Blocked("Nome de anexo inválido.")

    return request, {
        "process": process,
        "filename": name,
        "attachment_bytes": len(attachment),
        "attachment_sha256": hashlib.sha256(attachment).hexdigest(),
        "summary": "Verificar a integridade de " + name + ".",
        "parser": parsed.parser,
    }


class NexusHTTPServer(ThreadingHTTPServer):
    # Windows SO_REUSEADDR permits two listeners on the same address/port.
    allow_reuse_address = os.name != "nt"

    def server_bind(self):
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def make_server(host, port=0):
    preexecution_tickets = {}
    preexecution_lock = threading.Lock()

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
                    return self.reply(200, host.detail(path.split("/")[-1], session))
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
                    # Technical/manual route retained for diagnostics and existing tests.
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
