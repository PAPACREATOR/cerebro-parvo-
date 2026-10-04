import os
import sys
from pathlib import Path

import pytest

from nexus.contracts import Blocked
from nexus.mcp_client import MCPServerSpec, call_tool, list_tools
from nexus.tiny_classifier import TinySpec, classify

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable).resolve()


def mcp_spec():
    return MCPServerSpec(
        command=str(PYTHON),
        args=("-u", str(ROOT / "tests/fixtures/mcp_test_server.py")),
    )


def tiny_spec(timeout=3):
    return TinySpec(
        executable=str(PYTHON),
        args=("-u", str(ROOT / "tests/fixtures/tiny_classifier_process.py")),
        timeout=timeout,
    )


def test_mcp_real_stdio_discovers_tools_dynamically():
    tools = {item["name"] for item in list_tools(mcp_spec())}
    assert tools == {"ping", "second", "explode"}


def test_mcp_real_stdio_call_roundtrip():
    result = call_tool(mcp_spec(), "ping", {"value": "olá 日本語"}, allowed_tools={"ping"})
    assert result == {"echo": "olá 日本語", "authority": "NONE"}


def test_mcp_allowlist_blocks_before_execution():
    with pytest.raises(Blocked, match="não autorizada"):
        call_tool(mcp_spec(), "second", {"value": 5}, allowed_tools={"ping"})


def test_mcp_missing_tool_is_blocked():
    with pytest.raises(Blocked, match="não existe"):
        call_tool(mcp_spec(), "missing", {}, allowed_tools={"missing"})


def test_mcp_tool_error_is_blocked():
    with pytest.raises(Blocked, match="devolveu erro"):
        call_tool(mcp_spec(), "explode", {}, allowed_tools={"explode"})


@pytest.mark.parametrize(("marker", "intent"), [
    ("WEB", "web"), ("FONTES", "fontes"), ("TRABALHAR", "trabalhar"),
    ("PERGUNTAR", "perguntar"), ("CALCULAR", "calcular"),
    ("TEMA", "tema"), ("ARQUIVO", "arquivo"),
])
def test_tiny_local_process_classifies_only_allowed_intents(marker, intent):
    assert classify("pedido " + marker, tiny_spec()) == [intent]


def test_tiny_ambiguity_returns_no_hint():
    assert classify("WEB TRABALHAR", tiny_spec()) == []


def test_tiny_malformed_output_is_blocked():
    with pytest.raises(Blocked):
        classify("MALFORMED", tiny_spec())


def test_tiny_authority_injection_is_blocked():
    with pytest.raises(Blocked):
        classify("INJECT", tiny_spec())


def test_tiny_timeout_is_blocked():
    with pytest.raises(Blocked):
        classify("TIMEOUT", tiny_spec(timeout=1))


def test_tiny_executable_must_be_absolute_real_file():
    with pytest.raises(Blocked):
        classify("WEB", TinySpec("python", ()))
