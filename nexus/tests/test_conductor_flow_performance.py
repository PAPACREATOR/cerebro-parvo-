"""Empirical Conductor flow-performance probes for Nexus Lab.

Experimental benchmark only. The normal Nexus suite skips this module unless
NEXUS_CONDUCTOR_PERF=1 is explicitly set by the dedicated Lab workflow.
"""
from __future__ import annotations

import asyncio
import json
import os
import statistics
import sys
import time

import pytest
from conductor.config.schema import (
    ContextConfig,
    ForEachDef,
    LimitsConfig,
    ParallelGroup,
    RouteDef,
    RuntimeConfig,
    ScriptStepDef,
    SetStepDef,
    WorkflowConfig,
    WorkflowDef,
)
from conductor.engine.workflow import WorkflowEngine

if os.environ.get("NEXUS_CONDUCTOR_PERF") != "1":
    pytest.skip("Conductor performance Lab is opt-in", allow_module_level=True)


def engine(config: WorkflowConfig) -> WorkflowEngine:
    return WorkflowEngine(config)


async def timed_runs(config: WorkflowConfig, payload: dict, runs: int) -> list[float]:
    samples = []
    for _ in range(runs):
        start = time.perf_counter()
        await engine(config).run(payload)
        samples.append(time.perf_counter() - start)
    return samples


def stats(samples: list[float]) -> dict[str, float]:
    return {
        "median_ms": round(statistics.median(samples) * 1000, 3),
        "mean_ms": round(statistics.mean(samples) * 1000, 3),
        "min_ms": round(min(samples) * 1000, 3),
        "max_ms": round(max(samples) * 1000, 3),
    }


def emit(name: str, baseline: list[float], candidate: list[float]) -> None:
    b = statistics.median(baseline)
    c = statistics.median(candidate)
    improvement = ((b - c) / b * 100.0) if b else 0.0
    print("PERF " + json.dumps({
        "case": name,
        "baseline": stats(baseline),
        "candidate": stats(candidate),
        "median_improvement_pct": round(improvement, 2),
        "speedup_x": round((b / c), 3) if c else None,
    }, sort_keys=True))


def compact_set_config() -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="compact-set",
            entry_point="derive",
            runtime=RuntimeConfig(provider="copilot"),
            context=ContextConfig(mode="accumulate"),
            limits=LimitsConfig(max_iterations=10),
        ),
        agents=[
            SetStepDef(
                name="derive",
                values={
                    "a": "{{ workflow.input.x }}",
                    "b": "{{ workflow.input.x }}-b",
                    "c": "{{ workflow.input.x }}-c",
                    "d": "{{ workflow.input.x }}-d",
                    "e": "{{ workflow.input.x }}-e",
                },
                routes=[RouteDef(to="$end")],
            )
        ],
        output={
            "a": "{{ derive.output.a }}",
            "b": "{{ derive.output.b }}",
            "c": "{{ derive.output.c }}",
            "d": "{{ derive.output.d }}",
            "e": "{{ derive.output.e }}",
        },
    )


def chained_set_config() -> WorkflowConfig:
    agents = []
    names = ["a", "b", "c", "d", "e"]
    for i, name in enumerate(names):
        suffix = "" if name == "a" else f"-{name}"
        target = names[i + 1] if i + 1 < len(names) else "$end"
        agents.append(
            SetStepDef(
                name=name,
                value="{{ workflow.input.x }}" + suffix,
                routes=[RouteDef(to=target)],
            )
        )
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="chained-set",
            entry_point="a",
            runtime=RuntimeConfig(provider="copilot"),
            context=ContextConfig(mode="accumulate"),
            limits=LimitsConfig(max_iterations=10),
        ),
        agents=agents,
        output={name: "{{ " + name + ".output }}" for name in names},
    )


def sequential_ten_sets_config() -> WorkflowConfig:
    agents = []
    for i in range(10):
        target = f"s{i+1}" if i < 9 else "$end"
        agents.append(
            SetStepDef(
                name=f"s{i}",
                value="{{ workflow.input.x }}-" + str(i),
                routes=[RouteDef(to=target)],
            )
        )
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="sequential-ten-set",
            entry_point="s0",
            limits=LimitsConfig(max_iterations=20),
        ),
        agents=agents,
        output={f"v{i}": "{{ s" + str(i) + ".output }}" for i in range(10)},
    )


def parallel_ten_sets_config() -> WorkflowConfig:
    agents = [
        SetStepDef(name=f"s{i}", value="{{ workflow.input.x }}-" + str(i))
        for i in range(10)
    ]
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="parallel-ten-set",
            entry_point="all_sets",
            limits=LimitsConfig(max_iterations=20),
        ),
        agents=agents,
        parallel=[
            ParallelGroup(
                name="all_sets",
                agents=[f"s{i}" for i in range(10)],
                failure_mode="all_or_nothing",
                routes=[RouteDef(to="$end")],
            )
        ],
        output={
            f"v{i}": "{{ all_sets.outputs.s" + str(i) + " }}"
            for i in range(10)
        },
    )


def foreach_set_config(max_concurrent: int) -> WorkflowConfig:
    inline = SetStepDef(name="copy", value="{{ item }}")
    return WorkflowConfig(
        workflow=WorkflowDef(
            name=f"foreach-set-{max_concurrent}",
            entry_point="setup",
            limits=LimitsConfig(max_iterations=200),
        ),
        agents=[
            SetStepDef(
                name="setup",
                value="{{ range(0, 100) | list | tojson }}",
                output_type="list",
                routes=[RouteDef(to="loop")],
            )
        ],
        for_each=[
            ForEachDef.model_validate({
                "name": "loop",
                "type": "for_each",
                "source": "setup.output",
                "as": "item",
                "agent": inline,
                "max_concurrent": max_concurrent,
                "failure_mode": "all_or_nothing",
                "routes": [{"to": "$end"}],
            })
        ],
        output={"items": "{{ loop.outputs | tojson }}"},
    )


def set_echo_config() -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="set-echo",
            entry_point="echo",
            limits=LimitsConfig(max_iterations=5),
        ),
        agents=[
            SetStepDef(
                name="echo",
                value="{{ workflow.input.value }}",
                output_type="string",
                routes=[RouteDef(to="$end")],
            )
        ],
        output={"value": "{{ echo.output }}"},
    )


def script_echo_config() -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="script-echo",
            entry_point="echo",
            limits=LimitsConfig(max_iterations=5, timeout_seconds=5),
        ),
        agents=[
            ScriptStepDef(
                name="echo",
                command=sys.executable,
                args=["-c", "print(r'''{{ workflow.input.value }}''')"],
                timeout=3,
                routes=[RouteDef(to="$end")],
            )
        ],
        output={"value": "{{ echo.output.stdout | trim }}"},
    )


def test_perf_compact_set_vs_five_step_chain():
    async def run():
        payload = {"x": "nexus"}
        chain = chained_set_config()
        compact = compact_set_config()
        assert await engine(chain).run(payload) == await engine(compact).run(payload)
        baseline = await timed_runs(chain, payload, 200)
        candidate = await timed_runs(compact, payload, 200)
        emit("five_set_chain_vs_one_multi_set", baseline, candidate)
    asyncio.run(run())


def test_perf_parallel_ten_sets_vs_sequential():
    async def run():
        payload = {"x": "nexus"}
        sequential = sequential_ten_sets_config()
        parallel = parallel_ten_sets_config()
        assert await engine(sequential).run(payload) == await engine(parallel).run(payload)
        baseline = await timed_runs(sequential, payload, 100)
        candidate = await timed_runs(parallel, payload, 100)
        emit("ten_internal_sets_sequential_vs_parallel", baseline, candidate)
    asyncio.run(run())


def test_perf_foreach_set_concurrency_1_vs_20():
    async def run():
        serial = foreach_set_config(1)
        concurrent = foreach_set_config(20)
        assert await engine(serial).run({}) == await engine(concurrent).run({})
        baseline = await timed_runs(serial, {}, 30)
        candidate = await timed_runs(concurrent, {}, 30)
        emit("foreach_100_internal_sets_concurrency_1_vs_20", baseline, candidate)
    asyncio.run(run())


def test_perf_internal_set_vs_script_subprocess():
    async def run():
        payload = {"value": "ação-日本語-Nexus"}
        script = script_echo_config()
        internal = set_echo_config()
        assert await engine(script).run(payload) == await engine(internal).run(payload)
        baseline = await timed_runs(script, payload, 50)
        candidate = await timed_runs(internal, payload, 50)
        emit("script_subprocess_vs_internal_set", baseline, candidate)
    asyncio.run(run())
