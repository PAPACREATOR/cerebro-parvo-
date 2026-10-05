"""Minimal deterministic Nexus executor through local MCP.

The Kernel selects one of four Host-authorized processes. MCP is transport only:
no model, agent, reasoning or authority is present in this executor.
"""
import hashlib
import json
import os
import subprocess
import tempfile
import uuid
import sys
from pathlib import Path

# Load the known package directly: LPAC can read Nexus without being granted
# directory listing/read access to the repository or the human's parent folder.
if __package__ in (None, ""):
    import importlib.util
    package_root = Path(__file__).absolute().parents[1]
    package_spec = importlib.util.spec_from_file_location(
        "nexus", package_root / "__init__.py",
        submodule_search_locations=[str(package_root)])
    package = importlib.util.module_from_spec(package_spec)
    sys.modules["nexus"] = package
    package_spec.loader.exec_module(package)

from nexus.contracts import Blocked, ROOT, strict_json, validate
from nexus.mcp_client import MCPServerSpec, call_tool


PROCESS_TO_TOOL = {
    "verify": "verify_file",
    "interpret": "interpret_file",
    "proofread": "proofread_file",
    "convert_pdf": "convert_pdf_file",
}

PROCESS_FILES = {
    "verify": (
        "adapters/runner.py", "mcp_client.py", "mcp_tools_server.py",
        "adapters/verify_direct.py", "adapters/tools.py",
    ),
    "interpret": (
        "adapters/runner.py", "mcp_client.py", "mcp_tools_server.py",
        "adapters/notebook.py",
    ),
    "proofread": (
        "adapters/runner.py", "mcp_client.py", "mcp_tools_server.py",
        "adapters/languagetool.py",
    ),
    "convert_pdf": (
        "adapters/runner.py", "mcp_client.py", "mcp_tools_server.py",
        "adapters/office.py",
    ),
}


def process_fingerprint(process):
    files = PROCESS_FILES.get(process)
    if files is None:
        raise Blocked("Processo indisponível.")
    h = hashlib.sha256()
    h.update(process.encode("utf-8"))
    h.update(b"\0")
    for relative in (*files, "windows_sandbox.py", "native_mcp.py"):
        path = ROOT / relative
        h.update(relative.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def _trace(process, tool):
    return {
        "engine": "nexus/python-mcp",
        "version": "1.0.0",
        "process": process,
        "summary": {
            "usage": {"total_tokens": 0},
            "agents_executed": [tool],
        },
        "events": [{"type": "mcp.tool.completed", "step": tool}],
    }



def prepare_task(process, input_path, work, *, config_root=None):
    """Trusted Host preparation: selected input copies, RO tools, no Store access."""
    if process not in PROCESS_TO_TOOL:
        raise Blocked("Processo indisponível.")
    source, work = Path(input_path), Path(work)
    raw = source.read_bytes()
    if not raw or len(raw) > 2_097_152:
        raise Blocked("Input fora do limite.")
    (work / "input.bin").write_bytes(raw)
    roots = [ROOT, Path(sys.prefix), Path(sys.base_prefix)]
    # Private TemporaryDirectory ancestors need read access for Windows path
    # normalization. This grants only this freshly assigned task subtree.
    if work.parent.name != "runs" or not work.parent.parent.name.startswith(".nexus-task-"):
        raise Blocked("Área de tarefa não autorizada.")
    roots.append(work.parent.parent)
    config_root = Path(config_root) if config_root is not None else source.parent
    if process == "interpret":
        from nexus.adapters.notebook import fetch_output, prepare_source
        if not (config_root / "open-notebook.json").is_file():
            raise Blocked("A interpretação precisa da bancada local configurada.")
        config = strict_json((config_root / "open-notebook.json").read_bytes())
        response = fetch_output(prepare_source(raw), config)
        (work / "open-notebook-response.json").write_text(
            json.dumps(response, ensure_ascii=False), encoding="utf-8")
    elif process in ("proofread", "convert_pdf"):
        name = "languagetool.json" if process == "proofread" else "libreoffice.json"
        if not (config_root / name).is_file():
            raise Blocked("A ferramenta precisa de configuração local.")
        config = strict_json((config_root / name).read_bytes())
        keys = {"java", "jar"} if process == "proofread" else {"executable"}
        if not isinstance(config, dict) or set(config) != keys:
            raise Blocked("Configuração da ferramenta inválida.")
        for value in config.values():
            if not isinstance(value, str) or not Path(value).is_absolute() or not Path(value).is_file():
                raise Blocked("Ferramenta local indisponível.")
        if process == "proofread":
            java, jar = Path(config["java"]), Path(config["jar"])
            if java.name.lower() != "java.exe" or jar.name != "languagetool-commandline.jar":
                raise Blocked("Ferramenta não autorizada.")
            roots += [java.parent.parent, jar.parent]
        else:
            exe = Path(config["executable"])
            if exe.name.lower() != "soffice.com":
                raise Blocked("Ferramenta não autorizada.")
            roots.append(exe.parent.parent)
        (work / name).write_text(json.dumps(config), encoding="utf-8")
    return tuple(dict.fromkeys(roots))


def collect_artifact(envelope, work, destination):
    """Only after the job has ended; copy a fixed, bounded and hash-checked PDF."""
    validate("result", envelope["result"])
    artifact = envelope["result"].get("artifact")
    if artifact:
        from nexus.adapters.office import pdf_bytes
        path = Path(work) / "resultado.pdf"
        if path.is_junction() or path.resolve().parent != Path(work).resolve():
            raise Blocked("Artefacto redirecionado.")
        data = pdf_bytes(path)
        if artifact["name"] != "resultado.pdf" or hashlib.sha256(data).hexdigest() != artifact["sha256"]:
            raise Blocked("Artefacto não corresponde à resposta.")
        from nexus.store import atomic
        atomic(Path(destination) / "resultado.pdf", data)


def execute_confined(process, input_path):
    """Safe direct CLI entry; the Host uses the same preparation and native launch."""
    from nexus.windows_sandbox import launch_confined, task_environment
    path = Path(input_path).resolve()
    with tempfile.TemporaryDirectory(prefix=".nexus-task-", dir=path.parent.parent.parent.parent) as temporary:
        work = Path(temporary) / "runs" / uuid.uuid4().hex
        work.mkdir(parents=True)
        roots = prepare_task(process, path, work)
        command = [sys.executable, "-I", str(ROOT / "adapters/runner.py"), process, str(work / "input.bin")]
        with launch_confined(command, cwd=work, env=task_environment(work), read_roots=roots,
                             deny_roots=(path.parent.parent.parent,)) as proc:
            stdout, stderr = proc.communicate(timeout=150 if process == "interpret" else 75)
            code = proc.returncode
        if code:
            raise Blocked("A execução protegida falhou.")
        envelope = strict_json(stdout)
        if not isinstance(envelope, dict) or set(envelope) != {"result", "trace"}:
            raise Blocked("Resposta de execução inválida.")
        collect_artifact(envelope, work, path.parent)
        return envelope

def execute(process, input_path):
    if os.name == "nt":
        from nexus.windows_sandbox import inside_native_boundary
        if not inside_native_boundary():
            return execute_confined(process, input_path)
    tool = PROCESS_TO_TOOL.get(process)
    if tool is None:
        raise Blocked("Processo indisponível.")
    path = Path(input_path).resolve()
    server = MCPServerSpec(
        command=sys.executable,
        args=("-I", str(ROOT / "mcp_tools_server.py")),
    )
    result = call_tool(
        server,
        tool,
        {"input_path": str(path)},
        allowed_tools={tool},
    )
    return {"result": result, "trace": _trace(process, tool)}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        process, input_path = sys.argv[1:3]
        print(json.dumps(execute(process, input_path), ensure_ascii=False))
    except Exception:
        print("Execução MCP determinística indisponível ou resposta rejeitada.", file=sys.stderr)
        raise SystemExit(1)
