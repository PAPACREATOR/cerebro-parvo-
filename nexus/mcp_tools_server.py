"""Nexus-owned deterministic MCP tool server.

Transport only. No model, agent, memory, approval or Store access.
Each tool delegates to an already-bounded adapter using a Kernel-supplied input
path. Authority remains in Host/Store.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP

from nexus.adapters.verify_direct import execute as verify
from nexus.adapters.notebook import run as interpret
from nexus.adapters.languagetool import run as proofread
from nexus.adapters.office import run as convert_pdf
from nexus.contracts import Blocked


mcp = FastMCP("nexus-local-tools")


def _input(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise Blocked("Input MCP inválido.")
    path = Path(value)
    if not path.is_absolute() or path.name != "input.bin" or not path.is_file():
        raise Blocked("Input MCP não autorizado.")
    parent = path.parent
    if parent.name == "" or parent.parent.name != "runs":
        raise Blocked("Input MCP fora de um run Nexus.")
    return path.resolve()


@mcp.tool()
def verify_file(input_path: str) -> dict:
    return verify(_input(input_path))["result"]


@mcp.tool()
def interpret_file(input_path: str) -> dict:
    return interpret(_input(input_path))


@mcp.tool()
def proofread_file(input_path: str) -> dict:
    return proofread(_input(input_path))


@mcp.tool()
def convert_pdf_file(input_path: str) -> dict:
    return convert_pdf(_input(input_path))


if __name__ == "__main__":
    mcp.run(transport="stdio")
