import sys
from pathlib import Path

import pytest

from nexus.contracts import Blocked
from nexus.mcp_client import MCPServerSpec, call_tool, list_tools

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable).resolve()


def spec():
    return MCPServerSpec(
        command=str(PYTHON),
        args=("-u", str(ROOT / "tests/fixtures/mcp_test_server.py")),
    )


def test_real_mcp_discovers_tools():
    names = {item["name"] for item in list_tools(spec())}
    assert names == {"ping", "double", "explode"}


def test_real_mcp_bidirectional_unicode_roundtrip():
    original = "olá ação 日本語"
    result = call_tool(spec(), "ping", {"value": original}, allowed_tools={"ping"})
    assert result == {"echo": original, "authority": "NONE"}
    assert result["echo"].encode("utf-8") == original.encode("utf-8")


def test_mcp_allowlist_blocks_before_call():
    with pytest.raises(Blocked, match="não autorizada"):
        call_tool(spec(), "double", {"value": 5}, allowed_tools={"ping"})


def test_mcp_missing_tool_is_blocked():
    with pytest.raises(Blocked, match="não existe"):
        call_tool(spec(), "missing", {}, allowed_tools={"missing"})


def test_mcp_tool_error_is_blocked():
    with pytest.raises(Blocked, match="devolveu erro"):
        call_tool(spec(), "explode", {}, allowed_tools={"explode"})


def test_mcp_cloud_credentials_are_rejected():
    bad = MCPServerSpec(
        command=str(PYTHON),
        args=("-u", str(ROOT / "tests/fixtures/mcp_test_server.py")),
        env={"OPENAI_API_KEY": "forbidden"},
    )
    with pytest.raises(Blocked, match="Credencial cloud"):
        list_tools(bad)
