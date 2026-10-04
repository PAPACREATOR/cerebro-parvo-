"""Deterministic local MCP boundary for Nexus.

MCP is transport only. No model, agent or reasoning is used here.
The Kernel chooses the tool and arguments; this module only discovers and
executes explicitly allowed local MCP tools.
"""
from __future__ import annotations

import asyncio
import json
import os
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import Any, Iterable

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from nexus.contracts import Blocked


MAX_RESULT_BYTES = 1_000_000
BLOCKED_ENV_KEYS = {
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
}


@dataclass(frozen=True)
class MCPServerSpec:
    command: str
    args: tuple[str, ...]
    env: dict[str, str] | None = None


def _reduced_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env: dict[str, str] = {}
    for key in ("SystemRoot", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP", "PYTHONPATH"):
        value = os.environ.get(key)
        if value:
            env[key] = value
    if extra:
        for key, value in extra.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise TypeError("MCP env must contain strings")
            if key.upper() in BLOCKED_ENV_KEYS:
                raise Blocked("Credencial cloud proibida na fronteira MCP Nexus.")
            env[key] = value
    return env


async def _open_session(stack: AsyncExitStack, spec: MCPServerSpec) -> ClientSession:
    params = StdioServerParameters(
        command=spec.command,
        args=list(spec.args),
        env=_reduced_env(spec.env),
    )
    read, write = await stack.enter_async_context(stdio_client(params))
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    return session


async def list_tools_async(spec: MCPServerSpec) -> list[dict[str, Any]]:
    async with AsyncExitStack() as stack:
        session = await _open_session(stack, spec)
        response = await session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]


def _payload_from_result(result) -> dict[str, Any]:
    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        payload = structured
    else:
        texts = [
            part.text for part in result.content
            if getattr(part, "type", None) == "text"
        ]
        if len(texts) != 1:
            raise Blocked("Resposta MCP sem envelope único.")
        try:
            payload = json.loads(texts[0])
        except (TypeError, ValueError) as error:
            raise Blocked("Resposta MCP não é JSON estruturado.") from error

    if not isinstance(payload, dict):
        raise Blocked("Resposta MCP deve ser objeto JSON.")
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(raw) > MAX_RESULT_BYTES:
        raise Blocked("Resposta MCP excede o limite Nexus.")
    return payload


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

    pending_error: Blocked | None = None
    payload: dict[str, Any] | None = None

    async with AsyncExitStack() as stack:
        session = await _open_session(stack, spec)
        try:
            available = {tool.name for tool in (await session.list_tools()).tools}
            if tool_name not in available:
                pending_error = Blocked("Tool MCP não existe no servidor.")
            else:
                result = await session.call_tool(tool_name, arguments)
                if result.isError:
                    pending_error = Blocked("Tool MCP devolveu erro.")
                else:
                    payload = _payload_from_result(result)
        except Blocked as error:
            pending_error = error
        except Exception as error:
            pending_error = Blocked("Tool MCP falhou de forma controlada.")

    if pending_error is not None:
        raise pending_error
    if payload is None:
        raise Blocked("Tool MCP terminou sem resultado.")
    return payload


def list_tools(spec: MCPServerSpec) -> list[dict[str, Any]]:
    return asyncio.run(list_tools_async(spec))


def call_tool(
    spec: MCPServerSpec,
    tool_name: str,
    arguments: dict[str, Any],
    *,
    allowed_tools: Iterable[str],
) -> dict[str, Any]:
    return asyncio.run(
        call_tool_async(
            spec,
            tool_name,
            arguments,
            allowed_tools=allowed_tools,
        )
    )
