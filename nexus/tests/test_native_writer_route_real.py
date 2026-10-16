"""Installed Writer through actual Windows Host/LPAC/Job and Human Gate."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
import zipfile

import pytest

from nexus.host import Host
from nexus.tests.test_reverse_flow import http

pytestmark = pytest.mark.skipif(
    os.name != "nt" or os.environ.get("NEXUS_REAL_WRITER") != "1",
    reason="Explicit installed Writer native Windows gate NOT RUN here")


def test_writer_ipc_namespace_observation_inside_native_boundary(tmp_path):
    """Observe Writer's pipe convention; this is no conversion PASS."""
    from nexus.windows_sandbox import launch_confined, task_environment
    work = tmp_path / "ipc-probe"
    work.mkdir()
    script = r'''
import ctypes as C, json, uuid
from ctypes import wintypes as W
k=C.WinDLL('kernel32',use_last_error=True)
k.CreateMutexW.argtypes=[C.c_void_p,W.BOOL,W.LPCWSTR]
k.CreateMutexW.restype=W.HANDLE
k.CreateNamedPipeW.argtypes=[W.LPCWSTR,W.DWORD,W.DWORD,W.DWORD,W.DWORD,W.DWORD,W.DWORD,C.c_void_p]
k.CreateNamedPipeW.restype=W.HANDLE
k.CloseHandle.argtypes=[W.HANDLE]
result={}
for namespace in ('legacy','LOCAL'):
    name='OSL_PIPE_nexus_diagnostic_'+uuid.uuid4().hex
    mutex=k.CreateMutexW(None,False,name)
    mutex_error=C.get_last_error()
    path='\\\\.\\pipe\\'+('LOCAL\\' if namespace=='LOCAL' else '')+name
    pipe=k.CreateNamedPipeW(path,3|0x40000000,4|2,255,4096,4096,0xffffffff,None)
    error=C.get_last_error()
    ok=pipe not in (None,C.c_void_p(-1).value)
    result[namespace]={'mutex_created':bool(mutex),'mutex_error':mutex_error,
                       'pipe_created':ok,'pipe_error':0 if ok else error}
    if ok: k.CloseHandle(pipe)
    if mutex: k.CloseHandle(mutex)
print(json.dumps(result))
'''
    with launch_confined([sys.executable, "-I", "-c", script], cwd=work,
                         env=task_environment(work), read_roots=(sys.prefix, sys.base_prefix)) as worker:
        stdout, stderr = worker.communicate(timeout=15)
        assert worker.returncode == 0, stderr.decode(errors="replace")
    observed = json.loads(stdout)
    print("Writer IPC namespace observation (LPAC unchanged): " + json.dumps(observed))
    assert observed["LOCAL"]["pipe_created"], observed


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
    sandy = Path(os.environ["SANDY_EXE"])
    assert sandy.is_file()
    (data / "libreoffice.json").write_text(
        json.dumps({"executable": str(executable), "sandy": str(sandy)}), encoding="utf-8")
    raw = document()
    host = Host(data)
    # Real product entry: the Folha requests interpretation and a one-use
    # ticket. No direct execution route or delegated authority is enabled.
    text = "& converter para pdf" if process == "convert_pdf" else "& exportar manuscrito para pdf"
    proposal = {"text": text, "filename": "original.odt",
                "attachment": base64.b64encode(raw).decode("ascii")}
    with http(host) as call:
        from urllib.error import HTTPError
        with pytest.raises(HTTPError) as forbidden:
            call("/api/run", {"process": process, **proposal})
        assert forbidden.value.code == 403
        prepared = call("/api/prepare-run", proposal)
        assert prepared["process"] == process
        assert prepared["filename"] == proposal["filename"]
        assert prepared["attachment_bytes"] == len(raw)
        assert call("/api/runs") == []
        run = call("/api/confirm-run", {"ticket": prepared["ticket"],
                                      "confirmed": True, **proposal})["run_id"]
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


def test_two_real_tools_verify_then_writer_each_with_own_human_gates(tmp_path, monkeypatch):
    """One ODT source, two independent Host runs; native verify + Sandy Writer.

    No pseudo-tool, no Store bypass. Each request is approved for execution,
    validated into Creative, then independently promoted to Canonical.
    """
    from urllib.error import HTTPError
    from nexus.adapters.constitutional import build_molde
    from nexus.contracts import Blocked
    from nexus.lab.wiki.kernel_bridge import WikiBridge
    from nexus.lab.wiki.procedural_memory import ProceduralMemory

    data = tmp_path / "two-tools"
    data.mkdir()
    executable = Path(os.environ["LIBREOFFICE_EXE"])
    sandy = Path(os.environ["SANDY_EXE"])
    assert executable.is_file() and sandy.is_file()
    (data / "libreoffice.json").write_text(
        json.dumps({"executable": str(executable), "sandy": str(sandy)}),
        encoding="utf-8",
    )
    host = Host(data)
    raw = document()
    encoded = base64.b64encode(raw).decode("ascii")
    original = {"filename": "source.odt", "attachment": encoded}

    def finish(call, text):
        proposal = {"text": text, **original}
        prepared = call("/api/prepare-run", proposal)
        assert prepared["attachment_sha256"] == hashlib.sha256(raw).hexdigest()
        run = call("/api/confirm-run", {
            "ticket": prepared["ticket"], "confirmed": True, **proposal,
        })["run_id"]
        deadline = time.monotonic() + 90
        state = call("/api/runs/" + run)
        while state["status"] == "RUNNING" and time.monotonic() < deadline:
            time.sleep(0.1)
            state = call("/api/runs/" + run)
        assert state["status"] == "HUMAN_REQUIRED", state
        assert not (data / "canonical" / run).exists()
        approved = call("/api/prepare", {"run_id": run})
        assert call("/api/approve", {
            "run_id": run, "ticket": approved["ticket"], "confirmed": True,
        })["status"] == "PASS"
        assert (data / "runs" / run / "input.bin").read_bytes() == raw
        return run

    with http(host) as call:
        # The ONE free-text request must originate the bounded, read-only
        # Shell plan. The ordinary user-gated client performs each declared
        # operation; neither plan nor memory can start or approve any step.
        original_intent = call("/api/interpret", {
            "text": "Verifica este documento e converte-o em PDF",
        })
        plan = original_intent["composite"]
        assert plan["execution"] == "NOT_AUTHORIZED"
        assert [step["process"] for step in plan["steps"]] == ["verify", "convert_pdf"]
        assert call("/api/runs") == []
        verify_run = finish(call, "& " + plan["steps"][0]["command"])
        assert not (data / "creative" / verify_run / "resultado.pdf").exists()

        writer_proposal = {"text": "& converter para pdf", **original}
        pending = call("/api/prepare-run", writer_proposal)
        with pytest.raises(HTTPError) as direct:
            call("/api/run", {"process": "convert_pdf", **writer_proposal})
        assert direct.value.code == 403
        assert call("/api/confirm-run", {
            "ticket": pending["ticket"], "confirmed": False, **writer_proposal,
        }) == {"status": "CANCELLED"}
        assert len(call("/api/runs")) == 1

        writer_run = finish(call, "& " + plan["steps"][1]["command"])
        assert writer_run != verify_run
        pdf = (data / "canonical" / writer_run / "resultado.pdf").read_bytes()
        assert pdf.startswith(b"%PDF-") and b"%%EOF" in pdf[-1024:]
        assert len(call("/api/runs")) == 2
        assert host.store.state(verify_run)["process_id"] == "verify"
        assert host.store.state(writer_run)["process_id"] == "convert_pdf"
        assert host.store.state(verify_run)["input_sha256"] == host.store.state(writer_run)["input_sha256"]
        assert hashlib.sha256(pdf).hexdigest() == host.store.state(writer_run)["artifact_sha256"]
        host.store.check_commit(host.store.state(verify_run))
        host.store.check_commit(host.store.state(writer_run))

        # Observe two independently executed, verified tools. Learning remains
        # advisory and cannot execute or approve a future tool call.
        learning_root = tmp_path / "learning"
        learner = ProceduralMemory(WikiBridge(host.store, learning_root))
        first_mold = build_molde("& converter para pdf", "source.odt", encoded, intent="trabalhar")
        review = dict(
            goal="convert_pdf", steps=["verify", "convert_pdf"],
            phrase="verifica este ODT e converte para PDF",
            source_ids=[verify_run, writer_run],
            objective="Sequencia real verificada de ODT para PDF",
            decision="ACCEPT",
        )
        with pytest.raises(Blocked, match="Revisão humana"):
            learner.review(first_mold, **review, human_confirmed=False)
        assert not list(learner.root.iterdir())
        receipt = learner.review(first_mold, **review, human_confirmed=True)
        assert receipt["execution"] == "NOT_AUTHORIZED"
        assert receipt["authority"] == "NONE"

        # Completely new source: same document type, different bytes and text.
        stream = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(raw)) as source, zipfile.ZipFile(stream, "w") as output:
            for info in source.infolist():
                member = source.read(info.filename)
                if info.filename == "content.xml":
                    needle = "Lisboa recebeu 12 caixas.".encode("utf-8")
                    assert member.count(needle) == 1
                    member = member.replace(needle, "Porto recebeu 13 caixas.".encode("utf-8"))
                output.writestr(info, member)
        raw2 = stream.getvalue()
        assert hashlib.sha256(raw2).hexdigest() != hashlib.sha256(raw).hexdigest()
        raw = raw2
        encoded = base64.b64encode(raw).decode("ascii")
        original = {"filename": "new-source.odt", "attachment": encoded}

        independent = build_molde("& converter para pdf", "new-source.odt",
                                   encoded, intent="trabalhar")
        recovered_learner = ProceduralMemory(WikiBridge(host.store, learning_root))
        proposed = recovered_learner.suggest(independent, goal="convert_pdf")
        assert proposed["execution"] == "NOT_AUTHORIZED"
        assert proposed["requires_human_review"] is True
        assert proposed["candidates"][0]["origin"] == "LEARNED"
        assert proposed["candidates"][0]["steps"] == ["verify", "convert_pdf"]
        assert set(proposed["candidates"][0]["canonical_source_ids"]) == {
            verify_run, writer_run,
        }

        # These are two NEW real Host executions with their own user-gate
        # tickets, not a call from procedural memory or a replay.
        verify_second = finish(call, "& " + plan["steps"][0]["command"])
        writer_second = finish(call, "& " + plan["steps"][1]["command"])
        assert len({verify_run, writer_run, verify_second, writer_second}) == 4
        assert host.store.state(verify_second)["input_sha256"] == host.store.state(writer_second)["input_sha256"]
        assert host.store.state(verify_second)["input_sha256"] != host.store.state(verify_run)["input_sha256"]
        other_pdf = (data / "canonical" / writer_second / "resultado.pdf").read_bytes()
        assert other_pdf.startswith(b"%PDF-") and b"%%EOF" in other_pdf[-1024:]
        assert hashlib.sha256(other_pdf).hexdigest() == host.store.state(writer_second)["artifact_sha256"]
        assert len(call("/api/runs")) == 4

    def no_repeat(*_args, **_kwargs):
        pytest.fail("Reopening must not re-execute either capability")
    monkeypatch.setattr("nexus.host.launch_confined", no_repeat)
    monkeypatch.setattr("nexus.adapters.writer_sandy.convert", no_repeat)
    restored = Host(data)
    for run_id in (verify_run, writer_run, verify_second, writer_second):
        restored.store.check_commit(restored.store.state(run_id))
        assert restored.store.state(run_id)["status"] == "PASS"
