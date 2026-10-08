"""Transport equivalence: adapters and native boundaries remain real.

OpenNotebook responses and Java/Writer CLI peers are deterministic fixtures,
not claims of a model, LanguageTool installation, or physical PC validation.
"""
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from nexus.adapters.runner import PROCESS_TO_TOOL, process_fingerprint
from nexus.contracts import Blocked, ROOT, validate
from nexus.tests import _direct_candidate as direct

SOURCE = "Lisboa recebeu 12 caixas."
PDF = b"%PDF-1.4\n% deterministic CLI fixture\n%%EOF\n"


@pytest.fixture(scope="module")
def cli_peers(tmp_path_factory):
    root = tmp_path_factory.mktemp("transport-cli-peers")
    # A real PE process exercises inherited token/Job and stdio. Only the
    # external tool's semantic output is substituted in this transport proof.
    definition = r'''
using System;
using System.IO;
public class Peer {
  public static int Main(string[] args) {
    if (Environment.GetEnvironmentVariable("OPENAI_API_KEY") != null) return 90;
    if (Path.GetFileName(Environment.GetCommandLineArgs()[0]).ToLowerInvariant() == "java.exe") {
      Console.Write("{\"software\":{\"name\":\"LanguageTool\",\"version\":\"fixture\"},\"language\":{\"name\":\"Portuguese\",\"code\":\"pt-PT\"},\"matches\":[],\"warnings\":{\"incompleteResults\":false}}");
    } else {
      int index = Array.IndexOf(args, "--outdir");
      if (index < 0) return 91;
      File.WriteAllBytes(Path.Combine(args[index+1], "resultado.pdf"), System.Text.Encoding.ASCII.GetBytes("%PDF-1.4\n% deterministic CLI fixture\n%%EOF\n"));
    }
    return 0;
  }
}
'''
    (root / "peer.cs").write_text(definition, encoding="utf-8")
    script = "param($source,$target); Add-Type -TypeDefinition (Get-Content -LiteralPath $source -Raw) -OutputAssembly $target -OutputType ConsoleApplication"
    (root / "build.ps1").write_text(script, encoding="utf-8")
    built = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-File",
                            str(root / "build.ps1"), str(root / "peer.cs"), str(root / "java.exe")],
                           capture_output=True, timeout=60)
    assert built.returncode == 0, built.stderr.decode(errors="replace")
    (root / "soffice.com").write_bytes((root / "java.exe").read_bytes())
    (root / "languagetool-commandline.jar").write_bytes(b"fixture, never loaded by a JVM")
    return root


def prepare(work, process, tools):
    source = work / "input.bin"
    text = "Consulta: imprensa portuguesa" if process == "web" else SOURCE
    if process == "music":
        text = "Tema: memória\nLetra: Volto à rua onde cresci.\nEstilo: folk português"
    raw = text.encode("utf-8")
    if process in {"convert_pdf", "book"}:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            for name, value in [("mimetype", "application/vnd.oasis.opendocument.text"),
                                ("content.xml", '<document xmlns="http://example.org">Ensaio</document>')]:
                archive.writestr(zipfile.ZipInfo(name, (2026, 10, 8, 0, 0, 0)), value)
        raw = stream.getvalue()
    source.write_bytes(raw)
    if process == "interpret":
        (work / "open-notebook-response.json").write_text(json.dumps({
            "output": json.dumps({"title": "Entrega", "summary": SOURCE, "quotes": [SOURCE]}),
            "model_id": "model:fixture", "transformation_id": "transformation:fixture"}), encoding="utf-8")
    elif process in {"video", "podcast", "visual_podcast"}:
        (work / "product-plan-response.json").write_text(json.dumps({
            "output": json.dumps({"title": "Entrega", "body": SOURCE, "steps": ["Rever"], "quotes": [SOURCE]}),
            "model_id": "model:fixture", "transformation_id": "transformation:fixture"}), encoding="utf-8")
    elif process == "proofread":
        (work / "languagetool.json").write_text(json.dumps({
            "java": str(tools / "java.exe"), "jar": str(tools / "languagetool-commandline.jar")}), encoding="utf-8")
    elif process in {"convert_pdf", "book"}:
        (work / "libreoffice.json").write_text(json.dumps({"executable": str(tools / "soffice.com")}), encoding="utf-8")
    return source


@pytest.mark.skipif(os.name != "nt", reason="A/B native Windows execution NOT RUN on this OS")
@pytest.mark.parametrize("process", sorted(PROCESS_TO_TOOL))
def test_all_internal_capabilities_across_real_native_mcp_and_direct(tmp_path, monkeypatch, cli_peers, process):
    from nexus.windows_sandbox import launch_confined, task_environment
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-host-only-secret")
    denied = tmp_path / "store"
    denied.mkdir()
    marker = denied / "canonical"
    marker.write_bytes(b"human-owned")
    results, inputs = [], []
    pinned = process_fingerprint(process)
    for name, script in [("A", ROOT / "adapters/runner.py"),
                         ("B", ROOT / "tests/_direct_candidate.py")]:
        work = tmp_path / (".nexus-task-" + name) / "runs" / ("a" * 32)
        work.mkdir(parents=True)
        source = prepare(work, process, cli_peers)
        raw = source.read_bytes()
        inputs.append(raw)
        with launch_confined([sys.executable, "-I", str(script), process, str(source)],
                             cwd=work, env=task_environment(work),
                             read_roots=(ROOT, sys.prefix, sys.base_prefix, work.parent.parent,
                                         cli_peers, Path(os.environ["SystemRoot"]) / "Microsoft.NET"),
                             deny_roots=(denied,)) as worker:
            stdout, stderr = worker.communicate(timeout=150 if process in {"interpret", "video", "podcast", "visual_podcast"} else 75)
            assert worker.returncode == 0, (name, process, stderr.decode(errors="replace"))
        result = validate("result", json.loads(stdout)["result"])
        assert source.read_bytes() == raw
        assert marker.read_bytes() == b"human-owned"
        assert result["ai_calls"] == int(process in {"interpret", "video", "podcast", "visual_podcast"})
        if process in {"book", "convert_pdf"}:
            assert (work / "resultado.pdf").read_bytes() == PDF
            assert result["artifact"]["sha256"] == hashlib.sha256(PDF).hexdigest()
        else:
            assert "artifact" not in result
        results.append(result)
    assert results[0] == results[1]
    assert inputs[0] == inputs[1]
    assert process_fingerprint(process) == pinned


@pytest.mark.parametrize("process", sorted(PROCESS_TO_TOOL))
def test_direct_dispatch_has_same_fixed_policy_and_controlled_exceptions(tmp_path, monkeypatch, process):
    work = tmp_path / "runs" / ("a" * 32)
    work.mkdir(parents=True)
    source = work / "input.bin"
    source.write_bytes(b"original")
    monkeypatch.setattr(direct, "os", type("Platform", (), {"name": "posix"}))
    called = []
    def failing(selected, path):
        called.append((selected, path.read_bytes()))
        raise RuntimeError("synthetic adapter exception")
    monkeypatch.setattr(direct, "_dispatch", failing)
    with pytest.raises(Blocked, match="controlada"):
        direct.execute(process, source)
    assert called == [(process, b"original")]


@pytest.mark.parametrize("value", [None, [], {"ai_calls": 0}, float("nan"), "{invalid-json"])
def test_direct_rejects_malformed_results(tmp_path, monkeypatch, value):
    source = tmp_path / "runs" / ("a" * 32) / "input.bin"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"original")
    monkeypatch.setattr(direct, "os", type("Platform", (), {"name": "posix"}))
    monkeypatch.setattr(direct, "_dispatch", lambda *_: value)
    with pytest.raises(Blocked):
        direct.execute("web", source)


def test_schema_valid_output_still_respects_independent_mcp_byte_limit(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from nexus.mcp_client import _payload_from_result
    source = tmp_path / "runs" / ("a" * 32) / "input.bin"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"original")
    payload = {"status": "UNKNOWN", "outcome": "candidate", "title": "x", "markdown": "x",
               "ai_calls": 0, "evidence": [{"capability": "x", "status": "UNKNOWN", "value": "á" * 100000}] * 6}
    validate("result", payload)
    with pytest.raises(Blocked, match="limite"):
        _payload_from_result(SimpleNamespace(structuredContent=payload))
    monkeypatch.setattr(direct, "os", type("Platform", (), {"name": "posix"}))
    monkeypatch.setattr(direct, "_dispatch", lambda *_: payload)
    with pytest.raises(Blocked, match="limite"):
        direct.execute("web", source)


@pytest.mark.parametrize("process", ["shell", "approve", "canonical", "unknown"])
def test_direct_cannot_choose_a_tool_outside_policy(tmp_path, process):
    with pytest.raises(Blocked, match="indisponível"):
        direct.execute(process, tmp_path / "input.bin")


def test_direct_rejects_traversal_and_redirected_input(tmp_path, monkeypatch):
    monkeypatch.setattr(direct, "os", type("Platform", (), {"name": "posix"}))
    called = []
    monkeypatch.setattr(direct, "_dispatch", lambda *_: called.append(True))
    target = tmp_path / "outside"
    target.write_bytes(b"protected")
    source = tmp_path / "runs" / ("a" * 32) / "input.bin"
    source.parent.mkdir(parents=True)
    try:
        source.symlink_to(target)
    except OSError:
        # Windows directory junctions are separately covered by the native gate.
        pass
    for path in [Path("../input.bin"), target, source]:
        with pytest.raises(Blocked):
            direct.execute("verify", path)
    assert not called
