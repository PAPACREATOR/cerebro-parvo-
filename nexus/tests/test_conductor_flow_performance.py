"""Empirical Conductor flow-performance probes for Nexus Lab.

These are comparative measurements, not architecture changes. Each pair performs
the same logical class of work using different Conductor flow shapes.
"""
from __future__ import annotations

import asyncio
import json
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
    WaitStepDef,
    WorkflowConfig,
    WorkflowDef,
)
from conductor.engine.workflow import WorkflowEngine


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


def emit(name: str, baseline: list[float], optimized: list[float]) -> None:
    b = statistics.median(baseline)
    o = statistics.median(optimized)
    improvement = ((b - o) / b * 100.0) if b else 0.0
    print("PERF " + json.dumps({
        "case": name,
        "baseline": stats(baseline),
        "optimized": stats(optimized),
        "median_improvement_pct": round(improvement, 2),
        "speedup_x": round((b / o), 3) if o else None,
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


def sequential_wait_config() -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="sequential-waits",
            entry_point="wait_a",
            limits=LimitsConfig(max_iterations=10, timeout_seconds=5),
        ),
        agents=[
            WaitStepDef(name="wait_a", duration="40ms", routes=[RouteDef(to="wait_b")]),
            WaitStepDef(name="wait_b", duration="40ms", routes=[RouteDef(to="$end")]),
        ],
        output={"done": "true"},
    )


def parallel_wait_config() -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="parallel-waits",
            entry_point="both",
            limits=LimitsConfig(max_iterations=10, timeout_seconds=5),
        ),
        agents=[
            WaitStepDef(name="wait_a", duration="40ms"),
            WaitStepDef(name="wait_b", duration="40ms"),
        ],
        parallel=[
            ParallelGroup(
                name="both",
                agents=["wait_a", "wait_b"],
                failure_mode="all_or_nothing",
                routes=[RouteDef(to="$end")],
            )
        ],
        output={"done": "true"},
    )


def foreach_wait_config(max_concurrent: int) -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name=f"foreach-{max_concurrent}",
            entry_point="setup",
            limits=LimitsConfig(max_iterations=100, timeout_seconds=10),
        ),
        agents=[
            SetStepDef(
                name="setup",
                values={"items": "{{ [1,2,3,4,5,6,7,8,9,10] }}"},
                routes=[RouteDef(to="loop")],
            )
        ],
        for_each=[
            ForEachDef(
                name="loop",
                type="for_each",
                source="setup.output.items",
                **{"as": "item"},
                agent=WaitStepDef(name="pause", duration="20ms"),
                max_concurrent=max_concurrent,
                failure_mode="all_or_nothing",
                routes=[RouteDef(to="$end")],
            )
        ],
        output={"done": "true"},
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


@pytest.mark.asyncio
async def test_perf_compact_set_vs_five_step_chain():
    payload = {"x": "nexus"}
    chain = chained_set_config()
    compact = compact_set_config()

    assert await engine(chain).run(payload) == await engine(compact).run(payload)

    baseline = await timed_runs(chain, payload, 200)
    optimized = await timed_runs(compact, payload, 200)
    emit("five_set_chain_vs_one_multi_set", baseline, optimized)


@pytest.mark.asyncio
async def test_perf_parallel_waits_vs_sequential():
    sequential = sequential_wait_config()
    parallel = parallel_wait_config()

    assert (await engine(sequential).run({}))["done"] is True
    assert (await engine(parallel).run({}))["done"] is True

    baseline = await timed_runs(sequential, {}, 20)
    optimized = await timed_runs(parallel, {}, 20)
    emit("two_independent_waits_sequential_vs_parallel", baseline, optimized)


@pytest.mark.asyncio
async def test_perf_foreach_concurrency_1_vs_10():
    serial = foreach_wait_config(1)
    concurrent = foreach_wait_config(10)

    assert (await engine(serial).run({}))["done"] is True
    assert (await engine(concurrent).run({}))["done"] is True

    baseline = await timed_runs(serial, {}, 10)
    optimized = await timed_runs(concurrent, {}, 10)
    emit("foreach_10_items_concurrency_1_vs_10", baseline, optimized)


@pytest.mark.asyncio
async def test_perf_internal_set_vs_script_subprocess():
    payload = {"value": "ação-日本語-Nexus"}
    script = script_echo_config()
    internal = set_echo_config()

    assert await engine(script).run(payload) == await engine(internal).run(payload)

    baseline = await timed_runs(script, payload, 50)
    optimized = await timed_runs(internal, payload, 50)
    emit("script_subprocess_vs_internal_set", baseline, optimized)
