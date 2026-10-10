"""Real loopback Nexus app/Host/Store behind optional Node gateway.

No modifications to the sealed Python runtime. The test uses temporary Store
data and never starts an external tool or promotes a result.
"""

import http.client
import json
import os
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest

from nexus.app import application


REPO = Path(__file__).resolve().parents[2]


def _unused_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _request(port, path, *, method="GET", token=None, payload=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    headers = {}
    if token is not None:
        headers["X-Nexus-Session"] = token
    raw = None
    if payload is not None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    try:
        connection.request(method, path, body=raw, headers=headers)
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js unavailable")
def test_gateway_forwards_to_real_host_and_one_store_without_modifying_core(tmp_path):
    with application(tmp_path / "memory") as (host, server):
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = _unused_port()
        env = dict(os.environ, PORT=str(port), NEXUS_BACKEND_PORT=str(server.server_port))
        gateway = subprocess.Popen(
            [shutil.which("node"), "server.js"], cwd=REPO, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            for _ in range(80):
                if gateway.poll() is not None:
                    pytest.fail("Optional gateway exited before opening loopback listener.")
                try:
                    code, payload = _request(port, "/")
                    if code == 200:
                        assert b"Folha Nexus" in payload
                        break
                except (ConnectionError, OSError):
                    time.sleep(0.05)
            else:
                pytest.fail("Optional gateway did not start.")

            status, _ = _request(port, "/api/runs")
            assert status == 403

            status, raw = _request(port, "/api/runs", token="wrong-session")
            assert status == 403
            assert b"error" in raw

            status, raw = _request(port, "/api/runs", token=host.session)
            assert status == 200
            assert json.loads(raw) == []

            text = "?? perguntar sobre a memória do Nexus"
            status, raw = _request(
                port, "/api/interpret", method="POST", token=host.session,
                payload={"text": text},
            )
            assert status == 200
            interpreted = json.loads(raw)
            assert interpreted["original"] == text
            assert interpreted["execution"] == "NOT_AUTHORIZED"

            status, raw = _request(
                port, "/api/approve", method="POST", token=host.session,
                payload={"run_id": "a" * 32, "ticket": "not-approved", "confirmed": True},
            )
            assert status == 403

            assert host.list_runs(host.session) == []
            assert not any((tmp_path / "memory" / "runs").iterdir())
        finally:
            gateway.terminate()
            try:
                gateway.wait(timeout=5)
            except subprocess.TimeoutExpired:
                gateway.kill()
                gateway.wait(timeout=5)
            server.shutdown()
            thread.join(timeout=5)
