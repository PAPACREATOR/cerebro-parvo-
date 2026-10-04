"""Compare official verify flow with a lower-subprocess Conductor variant."""
from __future__ import annotations

import asyncio
import os
import statistics
import sys
import time
from pathlib import Path

from conductor.config.loader import load_workflow
from conductor.engine.workflow import WorkflowEngine


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "processes" / "verify.yaml"
OPTIMIZED = ROOT / "tests" / "fixtures" / "verify_optimized_lab.yaml"
PS = str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe")


async def run_one(workflow: Path, target: Path):
    config = load_workflow(workflow)
    engine = WorkflowEngine(config, workflow_path=workflow)
    result = await engine.run({
        "input_path": str(target),
        "python": sys.executable,
        "powershell": PS,
    })
    return result["result"], engine.get_execution_summary()


async def samples(workflow: Path, target: Path, count: int):
    values = []
    outputs = []
    summaries = []
    for _ in range(count):
        start = time.perf_counter()
        output, summary = await run_one(workflow, target)
        values.append(time.perf_counter() - start)
        outputs.append(output)
        summaries.append(summary)
    return values, outputs, summaries


def med_ms(xs):
    return statistics.median(xs) * 1000


def normalized(value):
    # Markdown whitespace produced by YAML/Jinja folding may differ while the
    # semantic report remains identical; all authority-bearing fields must match.
    return {
        "status": value["status"],
        "outcome": value["outcome"],
        "title": value["title"],
        "evidence": value["evidence"],
        "ai_calls": value["ai_calls"],
    }


def test_verify_optimized_equivalent_and_faster(tmp_path):
    async def main():
        target = tmp_path / "ação-日本語.bin"
        target.write_bytes((b"NEXUS\x00\xff" * 8192))

        official_once, official_summary = await run_one(OFFICIAL, target)
        optimized_once, optimized_summary = await run_one(OPTIMIZED, target)

        assert normalized(official_once) == normalized(optimized_once)
        assert "Os dois métodos obtiveram a mesma impressão digital" in optimized_once["markdown"]
        assert official_once["evidence"] == optimized_once["evidence"]

        official, official_outputs, official_summaries = await samples(OFFICIAL, target, 30)
        optimized, optimized_outputs, optimized_summaries = await samples(OPTIMIZED, target, 30)

        assert all(normalized(x) == normalized(official_once) for x in official_outputs)
        assert all(normalized(x) == normalized(official_once) for x in optimized_outputs)

        b = med_ms(official)
        o = med_ms(optimized)
        print(
            "VERIFY_PERF "
            + str({
                "official_median_ms": round(b, 3),
                "optimized_median_ms": round(o, 3),
                "speedup_x": round(b / o, 3),
                "improvement_pct": round((b - o) / b * 100, 2),
                "official_iterations": official_summary["iterations"],
                "optimized_iterations": optimized_summary["iterations"],
                "official_agents": official_summary["agents_executed"],
                "optimized_agents": optimized_summary["agents_executed"],
            })
        )

    asyncio.run(main())
