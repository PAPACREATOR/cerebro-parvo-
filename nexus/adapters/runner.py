"""Minimal deterministic Nexus executor through local MCP.

The Kernel selects one of four Host-authorized processes. MCP is transport only:
no model, agent, reasoning or authority is present in this executor.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from nexus.contracts import Blocked, ROOT
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
    for relative in files:
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


def execute(process, input_path):
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
