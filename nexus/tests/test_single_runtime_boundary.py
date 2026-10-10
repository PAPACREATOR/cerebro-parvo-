"""Regression guard: the Folha must have only the sealed Nexus Python backend.

This protects against accidentally introducing a second HTTP executor with
independent run state, approval tickets or synthetic Canonical decisions.
The guard deliberately does not change Kernel, parser, Host or Store.
"""

import hashlib
import json
from pathlib import Path

NEXUS = Path(__file__).resolve().parents[1]
REPOSITORY = NEXUS.parent


def test_single_authoritative_http_runtime():
    assert (NEXUS / "app.py").is_file()
    assert (NEXUS / "host.py").is_file()
    assert (NEXUS / "store.py").is_file()
    assert not (REPOSITORY / "server.js").exists(), (
        "Do not deploy a second HTTP server bypassing Nexus Host/Store."
    )
    assert not (REPOSITORY / "package.json").exists(), (
        "Do not introduce a second root-level application launcher."
    )


def test_folha_html_matches_host_integrity_manifest():
    manifest = json.loads((NEXUS / "integrity.json").read_text(encoding="utf-8"))
    html = (NEXUS / "ui" / "index.html").read_bytes()
    assert hashlib.sha256(html).hexdigest() == manifest["ui/index.html"], (
        "The Folha HTML changed without the existing Host integrity seal."
    )


def test_no_unreviewed_platform_runtime_metadata():
    assert not (REPOSITORY / "metadata.json").exists(), (
        "Do not claim external AI/runtime capabilities outside Nexus policy."
    )
