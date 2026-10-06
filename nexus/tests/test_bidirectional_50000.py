"""50,000 bidirectional cases: 25k internal + 25k real external MCP calls.

Counts are explicit. External means a real stdio MCP server process and JSON-RPC
round-trip in one persistent session; mocks do not count as external calls.
"""
from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack
from pathlib import Path
import sys

from nexus.frontdoor import ParsedInput
from nexus.natural_bridge import (
    from_markdown,
    kernel_from_notebook_boundary,
    kernel_to_notebook,
    to_markdown,
)
from nexus.mcp_client import MCPServerSpec, _open_session, _payload_from_result

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable).resolve()

INTERNAL_CASES = 25_000
EXTERNAL_CALLS = 25_000
TOTAL_CASES = INTERNAL_CASES + EXTERNAL_CALLS


def _text(i: int) -> str:
    alphabets = (
        "ação memória proveniência",
        "日本語 dados",
        "Δλ matemática",
        "livro—capítulo",
        "[]{}!? 0123456789",
    )
    return f"{i:05d}|" + "|".join(
        part[(i + n) % len(part):] + part[:(i + n) % len(part)]
        for n, part in enumerate(alphabets)
    )


def test_internal_bidirectional_25000_exact_roundtrips():
    count = 0
    intents = ("arquivo", "web", "fontes", "trabalhar", "perguntar", "calcular", "tema")
    for i in range(INTERNAL_CASES):
        original = _text(i)
        parsed = ParsedInput(
            status="RESOLVED",
            intent=intents[i % len(intents)],
            original=original,
            content=original,
            parser="stress-explicit-v1",
            explicit=bool(i & 1),
        )
        markdown = to_markdown(parsed)
        decoded = from_markdown(markdown)
        assert decoded["text"].encode("utf-8") == original.encode("utf-8"), i
        assert decoded["intent"] == parsed.intent, i
        packet = kernel_to_notebook(markdown)
        restored_markdown = kernel_from_notebook_boundary(packet)
        assert restored_markdown.encode("utf-8") == markdown.encode("utf-8"), i
        assert from_markdown(restored_markdown)["text"] == original, i
        count += 1
    assert count == INTERNAL_CASES


def _spec() -> MCPServerSpec:
    return MCPServerSpec(
        command=str(PYTHON),
        args=("-u", str(ROOT / "tests/fixtures/mcp_test_server.py")),
    )


async def _external_25000() -> int:
    async with AsyncExitStack() as stack:
        session = await _open_session(stack, _spec())
        count = 0
        for i in range(EXTERNAL_CALLS):
            original = _text(i)
            result = await session.call_tool("ping", {"value": original})
            assert result.isError is False, i
            payload = _payload_from_result(result)
            assert payload == {"echo": original, "authority": "NONE"}, i
            assert payload["echo"].encode("utf-8") == original.encode("utf-8"), i
            count += 1
        return count


def test_external_mcp_real_stdio_25000_bidirectional_calls():
    count = asyncio.run(_external_25000())
    assert count == EXTERNAL_CALLS


def test_declared_total_is_exactly_50000():
    assert INTERNAL_CASES == 25_000
    assert EXTERNAL_CALLS == 25_000
    assert TOTAL_CASES == 50_000
