"""Minimal local MCP client boundary for Nexus.

Only stdio servers are supported here. Tool discovery is dynamic, but execution
is denied unless the caller supplies an explicit allowlist. MCP tools never gain
Nexus authority, approval, persistence or Canonical access.
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Iterable

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from nexus.contracts import Blocked


MAX_RESULT_BYTES = 1_000_000


@dataclass(frozen=True)
class MCPServerSpec:
    command: str
    args: tuple[str, ...]
    env: dict[str, str] | None = None


def _reduced_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    base = {}
    for key in ("SystemRoot", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP", "PYTHONPATH"):
        value = os.environ.get(key)
        if value:
            base[key] = value
    if extra:
        for key, value in extra.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise TypeError("MCP env must contain strings")
            if key.upper() in {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY"}:
                raise Blocked("Credenciais cloud não podem ser injetadas no MCP Nexus.")
            base[key] = value
    return base


async def _session(spec: MCPServerSpec):
    params = StdioServerParameters(
        command=spec.command,
        args=list(spec.args),
        env=_reduced_env(spec.env),
    )
    transport = stdio_client(params)
    read, write = await transport.__aenter__()
    session_ctx = ClientSession(read, write)
    session = await session_ctx.__aenter__()
    try:
        await session.initialize()
        return transport, session_ctx, session
    except BaseException:
        await session_ctx.__aexit__(None, None, None)
        await transport.__aexit__(None, None, None)
        raise


async def list_tools_async(spec: MCPServerSpec) -> list[dict[str, Any]]:
    transport, session_ctx, session = await _session(spec)
    try:
        response = await session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
    finally:
        await session_ctx.__aexit__(None, None, None)
        await transport.__aexit__(None, None, None)


async def call_tool_async(
    spec: MCPServerSpec,
    tool_name: str,
    arguments: dict[str, Any],
    *,
    allowed_tools: Iterable[str],
) -> dict[str, Any]:
    allow = frozenset(allowed_tools)
    if tool_name not in allow:
        raise Blocked("Tool MCP não autorizada pelo Kernel.")
    if not isinstance(arguments, dict):
        raise TypeError("MCP arguments must be dict")

    transport, session_ctx, session = await _session(spec)
    try:
        available = {tool.name for tool in (await session.list_tools()).tools}
        if tool_name not in available:
            raise Blocked("Tool MCP pedida não existe no servidor atual.")
        result = await session.call_tool(tool_name, arguments)
        if result.isError:
            raise Blocked("Tool MCP devolveu erro.")

        structured = getattr(result, "structuredContent", None)
        if structured is not None:
            payload = structured
        else:
            texts = [part.text for part in result.content if getattr(part, "type", None) == "text"]
            if len(texts) != 1:
                raise Blocked("Resposta MCP sem envelope único utilizável.")
            try:
                payload = json.loads(texts[0])
            except (ValueError, TypeError) as error:
                raise Blocked("Resposta MCP não é JSON estruturado.") from error

        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(raw) > MAX_RESULT_BYTES:
            raise Blocked("Resposta MCP excede o limite Nexus.")
        return payload
    finally:
        await session_ctx.__aexit__(None, None, None)
        await transport.__aexit__(None, None, None)


def list_tools(spec: MCPServerSpec) -> list[dict[str, Any]]:
    return asyncio.run(list_tools_async(spec))


def call_tool(spec: MCPServerSpec, tool_name: str, arguments: dict[str, Any], *, allowed_tools: Iterable[str]) -> dict[str, Any]:
    return asyncio.run(call_tool_async(spec, tool_name, arguments, allowed_tools=allowed_tools))
