"""Loopback-only Folha Nexus server using the Python standard library."""
import argparse
import json
import sys
import webbrowser
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from nexus.contracts import ROOT, Blocked, strict_json
from nexus.host import Host
from nexus.instance import data_directory_lock


def make_server(host, port=0):
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
                if path == "/api/run":
                    return self.reply(202, host.start(data, session))
                if path == "/api/prepare" and set(data) == {"run_id"}:
                    return self.reply(200, host.prepare_approval(data["run_id"], session))
                if path == "/api/approve" and set(data) == {"run_id", "ticket", "confirmed"}:
                    return self.reply(200, host.approve(data["run_id"], data["ticket"], data["confirmed"], session))
                raise Blocked("Operação não autorizada.")
            except (Blocked, ValueError, KeyError, FileNotFoundError) as error:
                self.reply(403, {"error": str(error)})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


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
            (host.store.root / "launch-url.txt").write_text(url, encoding="utf-8")
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
