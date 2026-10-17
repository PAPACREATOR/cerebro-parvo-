"""Consolidated real HTTP Host/Origin regression from the independent Folha lab.

Exercises the *production* Python Nexus Host on an ephemeral localhost port.
Never mocks the parser, dispatches a tool, or mutates Canonical. A syntactically
valid user request must not reach interpretation when browser headers are untrusted.
"""
from contextlib import contextmanager
import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from nexus.app import make_server
from nexus.host import Host


@contextmanager
def ephemeral_host(tmp_path):
    host = Host(tmp_path)
    server = make_server(host)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield host, "http://127.0.0.1:" + str(server.server_port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request(base, session, *, method, host_override=None, origin=None):
    headers = {"X-Nexus-Session": session}
    if host_override is not None:
        headers["Host"] = host_override
    if origin is not None:
        headers["Origin"] = origin
    if method == "POST":
        headers["Content-Type"] = "application/json"
        body = json.dumps({"text": "Guarda esta nota."}, ensure_ascii=False).encode("utf-8")
        path = "/api/interpret"
    else:
        body = None
        path = "/"
    try:
        with urlopen(Request(base + path, data=body, headers=headers, method=method), timeout=10) as reply:
            return reply.status, reply.read()
    except HTTPError as error:
        return error.code, error.read()


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("host_header", [
    "attacker.example",
    "attacker.example:8765",
    "localhost",
    "127.0.0.1",
    "127.0.0.1:9999",
])
def test_foreign_host_rejected_before_interpretation(tmp_path, method, host_header):
    with ephemeral_host(tmp_path) as (host, base):
        status, _ = request(base, host.session, method=method, host_override=host_header)
        assert status == 403
        assert host.list_runs(host.session) == []


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("origin", [
    "https://foreign.example",
    "http://foreign.example",
    "null",
    "http://127.0.0.1:9999",
    "https://127.0.0.1:9999",
])
def test_foreign_origin_rejected_before_interpretation(tmp_path, method, origin):
    with ephemeral_host(tmp_path) as (host, base):
        status, _ = request(base, host.session, method=method, origin=origin)
        assert status == 403
        assert host.list_runs(host.session) == []


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_exact_local_origin_remains_usable_without_execution(tmp_path, method):
    with ephemeral_host(tmp_path) as (host, base):
        status, raw = request(base, host.session, method=method, origin=base)
        assert status == 200
        if method == "POST":
            payload = json.loads(raw)
            assert payload["execution"] == "NOT_AUTHORIZED"
            assert payload["original"] == "Guarda esta nota."
        assert host.list_runs(host.session) == []
        assert not list((tmp_path / "canonical").iterdir())
