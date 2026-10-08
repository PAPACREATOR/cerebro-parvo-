"""Installed Writer through actual Windows Host/LPAC/Job and Human Gate."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import time
import zipfile

import pytest

from nexus.host import Host
from nexus.tests.test_reverse_flow import http

pytestmark = pytest.mark.skipif(
    os.name != "nt" or os.environ.get("NEXUS_REAL_WRITER") != "1",
    reason="Explicit installed Writer native Windows gate NOT RUN here")


def document():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        archive.writestr("content.xml", '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" office:version="1.3">'
            '<office:body><office:text><text:p>Lisboa recebeu 12 caixas.</text:p>'
            '</office:text></office:body></office:document-content>')
        archive.writestr("META-INF/manifest.xml", '<?xml version="1.0" encoding="UTF-8"?>'
            '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.3">'
            '<manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>'
            '<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>'
            '</manifest:manifest>')
    return stream.getvalue()


@pytest.mark.parametrize("process", ["book", "convert_pdf"])
def test_installed_writer_is_confined_and_returns_only_a_human_approved_candidate(tmp_path, monkeypatch, process):
    from nexus import host as host_module
    real_launch = host_module.launch_confined
    tool_diagnostics = []
    def observed_launch(command, **kwargs):
        kwargs["env"] = {**kwargs["env"], "SAL_LOG": "+WARN"}
        worker = real_launch(command, **kwargs)
        communicate = worker.communicate
        def observed_communication(*args, **options):
            try:
                return communicate(*args, **options)
            finally:
                work = Path(kwargs["cwd"])
                for name in ["office/stdout.txt", "office/stderr.txt"]:
                    path = work / name
                    if path.is_file():
                        tool_diagnostics.append({name: path.read_bytes()[:12000].decode("utf-8", errors="replace")})
        worker.communicate = observed_communication
        return worker
    monkeypatch.setattr(host_module, "launch_confined", observed_launch)
    executable = Path(os.environ["LIBREOFFICE_EXE"])
    assert executable.is_file()
    data = tmp_path / "data"
    data.mkdir()
    (data / "libreoffice.json").write_text(json.dumps({"executable": str(executable)}), encoding="utf-8")
    raw = document()
    host = Host(data)
    with http(host) as call:
        run = call("/api/run", {"process": process, "text": "", "filename": "original.odt",
                               "attachment": base64.b64encode(raw).decode("ascii")})["run_id"]
        deadline = time.monotonic() + 90
        state = call("/api/runs/" + run)
        while state["status"] == "RUNNING" and time.monotonic() < deadline:
            time.sleep(0.1)
            state = call("/api/runs/" + run)
        if state["status"] != "HUMAN_REQUIRED":
            folder = data / "runs" / run
            diagnostics = {p.name: p.read_text("utf-8", errors="replace")[-12000:]
                           for p in folder.iterdir() if p.suffix in {".json", ".txt"}}
            pytest.fail(json.dumps({"state": state, "diagnostics": diagnostics, "tool": tool_diagnostics}, ensure_ascii=False))
        assert state["result"]["status"] == "UNKNOWN"
        assert state["result"]["ai_calls"] == 0
        assert not (data / "canonical" / run).exists()
        assert (data / "runs" / run / "input.bin").read_bytes() == raw
        pdf = (data / "creative" / run / "resultado.pdf").read_bytes()
        assert pdf.startswith(b"%PDF-") and b"%%EOF" in pdf[-1024:]
        assert state["result"]["artifact"]["sha256"] == hashlib.sha256(pdf).hexdigest()
        ticket = call("/api/prepare", {"run_id": run})["ticket"]
        final = call("/api/approve", {"run_id": run, "ticket": ticket, "confirmed": True})
        assert final["status"] == "PASS"
    package = {p.name: p.read_bytes() for p in (data / "canonical" / run).iterdir()}
    assert package["resultado.pdf"] == pdf
    def no_replay(*args, **kwargs):
        pytest.fail("Restart replayed Writer or another tool")
    monkeypatch.setattr("nexus.host.launch_confined", no_replay)
    monkeypatch.setattr("nexus.adapters.office.run", no_replay)
    restored = Host(data)
    restored.store.check_commit(restored.store.state(run))
    assert restored.store.state(run)["status"] == "PASS"
    assert {p.name: p.read_bytes() for p in (data / "canonical" / run).iterdir()} == package
