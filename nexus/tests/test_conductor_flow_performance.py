"""Empirical Conductor flow-performance probes for the Nexus Lab.

Opt-in benchmark only. The normal Nexus suite skips this module unless
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
    ForEachDef,
    LimitsConfig,
    ParallelGroup,
    RouteDef,
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
    samples: list[float] = []
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
    print("PERF " + json.dumps({
        "case": name,
        "baseline": stats(baseline),
        "candidate": stats(candidate),
        "median_improvement_pct": round(((b - c) / b * 100.0) if b else 0.0, 2),
        "speedup_x": round((b / c), 3) if c else None,
    }, sort_keys=True))


def chained_set_config() -> WorkflowConfig:
    names = ["a", "b", "c", "d", "e"]
    agents = []
    for i, name in enumerate(names):
        suffix = "" if name == "a" else f"-{name}"
        agents.append(SetStepDef(
            name=name,
            value="{{ workflow.input.x }}" + suffix,
            routes=[RouteDef(to=names[i + 1] if i + 1 < len(names) else "$end")],
        ))
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="chain-five-set",
            entry_point="a",
            limits=LimitsConfig(max_iterations=10),
        ),
        agents=agents,
        output={name: "{{ " + name + ".output }}" for name in names},
    )


def compact_set_config() -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="compact-multi-set",
            entry_point="derive",
            limits=LimitsConfig(max_iterations=5),
        ),
        agents=[SetStepDef(
            name="derive",
            values={
                "a": "{{ workflow.input.x }}",
                "b": "{{ workflow.input.x }}-b",
                "c": "{{ workflow.input.x }}-c",
                "d": "{{ workflow.input.x }}-d",
                "e": "{{ workflow.input.x }}-e",
            },
            routes=[RouteDef(to="$end")],
        )],
        output={
            "a": "{{ derive.output.a }}",
            "b": "{{ derive.output.b }}",
            "c": "{{ derive.output.c }}",
            "d": "{{ derive.output.d }}",
            "e": "{{ derive.output.e }}",
        },
    )


def sequential_ten_sets_config() -> WorkflowConfig:
    agents = []
    for i in range(10):
        agents.append(SetStepDef(
            name=f"s{i}",
            value="{{ workflow.input.x }}-" + str(i),
            routes=[RouteDef(to=f"s{i + 1}" if i < 9 else "$end")],
        ))
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="sequential-ten-sets",
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
            name="parallel-ten-sets",
            entry_point="all_sets",
            limits=LimitsConfig(max_iterations=20),
        ),
        agents=agents,
        parallel=[ParallelGroup(
            name="all_sets",
            agents=[f"s{i}" for i in range(10)],
            failure_mode="all_or_nothing",
            routes=[RouteDef(to="$end")],
        )],
        output={
            f"v{i}": "{{ all_sets.outputs.s" + str(i) + " }}"
            for i in range(10)
        },
    )


def foreach_sets_config(max_concurrent: int) -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name=f"foreach-sets-{max_concurrent}",
            entry_point="setup",
            limits=LimitsConfig(max_iterations=200),
        ),
        agents=[SetStepDef(
            name="setup",
            values={"items": "{{ range(0, 100) | list | tojson }}"},
            routes=[RouteDef(to="loop")],
        )],
        for_each=[ForEachDef.model_validate({
            "name": "loop",
            "type": "for_each",
            "source": "setup.output.items",
            "as": "item",
            "max_concurrent": max_concurrent,
            "failure_mode": "all_or_nothing",
            "agent": {
                "name": "copy",
                "type": "set",
                "value": "{{ item }}",
            },
            "routes": [{"to": "$end"}],
        })],
        output={"items": "{{ loop.outputs | tojson }}"},
    )

def set_echo_config() -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="set-echo",
            entry_point="echo",
            limits=LimitsConfig(max_iterations=5),
        ),
        agents=[SetStepDef(
            name="echo",
            value="{{ workflow.input.value }}",
            output_type="string",
            routes=[RouteDef(to="$end")],
        )],
        output={"value": "{{ echo.output }}"},
    )


def script_echo_config() -> WorkflowConfig:
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="script-echo",
            entry_point="echo",
            limits=LimitsConfig(max_iterations=5, timeout_seconds=5),
        ),
        agents=[ScriptStepDef(
            name="echo",
            command=sys.executable,
            args=["-c", "print(r'''{{ workflow.input.value }}''')"],
            timeout=3,
            routes=[RouteDef(to="$end")],
        )],
        output={"value": "{{ echo.output.stdout | trim }}"},
    )


def test_perf_compact_set_vs_five_step_chain():
    async def run():
        payload = {"x": "nexus"}
        baseline_cfg = chained_set_config()
        candidate_cfg = compact_set_config()
        assert await engine(baseline_cfg).run(payload) == await engine(candidate_cfg).run(payload)
        emit(
            "five_set_chain_vs_one_multi_set",
            await timed_runs(baseline_cfg, payload, 200),
            await timed_runs(candidate_cfg, payload, 200),
        )
    asyncio.run(run())


def test_perf_parallel_internal_sets_vs_sequential():
    async def run():
        payload = {"x": "nexus"}
        baseline_cfg = sequential_ten_sets_config()
        candidate_cfg = parallel_ten_sets_config()
        assert await engine(baseline_cfg).run(payload) == await engine(candidate_cfg).run(payload)
        emit(
            "ten_internal_sets_sequential_vs_parallel",
            await timed_runs(baseline_cfg, payload, 100),
            await timed_runs(candidate_cfg, payload, 100),
        )
    asyncio.run(run())


def test_perf_foreach_internal_sets_concurrency_1_vs_20():
    async def run():
        baseline_cfg = foreach_sets_config(1)
        candidate_cfg = foreach_sets_config(20)
        assert await engine(baseline_cfg).run({}) == await engine(candidate_cfg).run({})
        emit(
            "foreach_100_internal_sets_concurrency_1_vs_20",
            await timed_runs(baseline_cfg, {}, 30),
            await timed_runs(candidate_cfg, {}, 30),
        )
    asyncio.run(run())


def test_perf_internal_set_vs_script_subprocess():
    async def run():
        payload = {"value": "ação-日本語-Nexus"}
        baseline_cfg = script_echo_config()
        candidate_cfg = set_echo_config()
        assert await engine(baseline_cfg).run(payload) == await engine(candidate_cfg).run(payload)
        emit(
            "script_subprocess_vs_internal_set",
            await timed_runs(baseline_cfg, payload, 50),
            await timed_runs(candidate_cfg, payload, 50),
        )
    asyncio.run(run())
