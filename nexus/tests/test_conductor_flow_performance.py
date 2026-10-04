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


def sequential_scripts_config() -> WorkflowConfig:
    sleeper = "import time; time.sleep(0.04); print('done')"
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="sequential-scripts",
            entry_point="a",
            limits=LimitsConfig(max_iterations=5, timeout_seconds=5),
        ),
        agents=[
            ScriptStepDef(
                name="a",
                command=sys.executable,
                args=["-c", sleeper],
                timeout=3,
                routes=[RouteDef(to="b")],
            ),
            ScriptStepDef(
                name="b",
                command=sys.executable,
                args=["-c", sleeper],
                timeout=3,
                routes=[RouteDef(to="$end")],
            ),
        ],
        output={"done": "true"},
    )


def parallel_scripts_config() -> WorkflowConfig:
    sleeper = "import time; time.sleep(0.04); print('done')"
    return WorkflowConfig(
        workflow=WorkflowDef(
            name="parallel-scripts",
            entry_point="both",
            limits=LimitsConfig(max_iterations=5, timeout_seconds=5),
        ),
        agents=[
            ScriptStepDef(name="a", command=sys.executable, args=["-c", sleeper], timeout=3),
            ScriptStepDef(name="b", command=sys.executable, args=["-c", sleeper], timeout=3),
        ],
        parallel=[ParallelGroup(
            name="both",
            agents=["a", "b"],
            failure_mode="all_or_nothing",
            routes=[RouteDef(to="$end")],
        )],
        output={"done": "true"},
    )


def foreach_scripts_config(max_concurrent: int) -> WorkflowConfig:
    sleeper = "import time; time.sleep(0.02); print('done')"
    return WorkflowConfig(
        workflow=WorkflowDef(
            name=f"foreach-scripts-{max_concurrent}",
            entry_point="setup",
            limits=LimitsConfig(max_iterations=50, timeout_seconds=10),
        ),
        agents=[SetStepDef(
            name="setup",
            value="{{ [1,2,3,4,5,6,7,8,9,10] | tojson }}",
            output_type="list",
            routes=[RouteDef(to="loop")],
        )],
        for_each=[ForEachDef.model_validate({
            "name": "loop",
            "type": "for_each",
            "source": "setup.output",
            "as": "item",
            "max_concurrent": max_concurrent,
            "failure_mode": "all_or_nothing",
            "agent": {
                "name": "pause",
                "type": "script",
                "command": sys.executable,
                "args": ["-c", sleeper],
                "timeout": 3,
            },
            "routes": [{"to": "$end"}],
        })],
        output={"count": "{{ loop.count }}"},
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


def test_perf_parallel_scripts_vs_sequential():
    async def run():
        baseline_cfg = sequential_scripts_config()
        candidate_cfg = parallel_scripts_config()
        assert (await engine(baseline_cfg).run({}))["done"] is True
        assert (await engine(candidate_cfg).run({}))["done"] is True
        emit(
            "two_script_sleeps_sequential_vs_parallel",
            await timed_runs(baseline_cfg, {}, 20),
            await timed_runs(candidate_cfg, {}, 20),
        )
    asyncio.run(run())


def test_perf_foreach_concurrency_1_vs_10():
    async def run():
        baseline_cfg = foreach_scripts_config(1)
        candidate_cfg = foreach_scripts_config(10)
        assert await engine(baseline_cfg).run({}) == await engine(candidate_cfg).run({})
        emit(
            "foreach_10_scripts_concurrency_1_vs_10",
            await timed_runs(baseline_cfg, {}, 10),
            await timed_runs(candidate_cfg, {}, 10),
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
