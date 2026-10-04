"""A/B/C Lab: same 500 seeded cases through Spiff-only, Conductor-only and Spiff->Conductor.

This is evidence only. It does not alter Kernel authority, Creative/Canonical or Human Gate.
"""
import asyncio
import hashlib
import random
import subprocess
import time
from pathlib import Path

import pytest

pytest.importorskip("SpiffWorkflow", reason="Spiff is an optional Lab executor")
from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import Simple, WorkflowSpec
from conductor.config.loader import load_workflow
from conductor.engine.workflow import WorkflowEngine

from nexus.tests.test_spiff_conductor_bidirectional_5000 import build_spiff_spec, kernel_execute

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "spiff_conductor_echo.yaml"
SEED = 20261004
CASES = 500


def _digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _cases():
    rng = random.Random(SEED)
    alphabet = "abcXYZ0123 áéç_日本語_-"
    states = ("PASS", "FAIL", "UNKNOWN", "BLOCKED")
    directions = ("forward", "reverse", "bounded", "classify")
    out = []
    for i in range(CASES):
        size = rng.randint(1, 300)
        payload = "".join(rng.choice(alphabet) for _ in range(size))
        out.append({
            "case_id": f"CMP-{i:04d}",
            "payload": payload,
            "input_hash": _digest(payload),
            "direction": directions[rng.randrange(len(directions))],
            "status": states[rng.randrange(len(states))],
            "ordinal": i,
        })
    return out


def _request(case):
    return {k: case[k] for k in ("case_id", "input_hash", "direction", "status", "ordinal")}


def _spiff_only(case):
    spec = WorkflowSpec("nexus-spiff-only", addstart=True)
    task = Simple(spec, "spiff_echo")
    spec.start.connect(task)

    def echo(workflow, _task):
        workflow.data["result"] = dict(workflow.data["request"])
        workflow.data["calls"] = workflow.data.get("calls", 0) + 1

    task.completed_event.connect(echo)
    workflow = Workflow(spec)
    workflow.set_data(request=_request(case), calls=0)
    workflow.run_all()
    assert workflow.is_completed()
    assert workflow.get_data("calls") == 1
    return workflow.get_data("result")


async def _conductor_async(config, case):
    engine = WorkflowEngine(config, workflow_path=FIXTURE)
    return await engine.run(_request(case))


def _conductor_only(config, case):
    return asyncio.run(_conductor_async(config, case))


def _joint(spec, case):
    out = kernel_execute(
        spec,
        case_id=case["case_id"], payload=case["payload"],
        direction=case["direction"], status=case["status"], ordinal=case["ordinal"],
    )
    assert out["reverse"]["case_id"] == case["case_id"]
    assert out["reverse"]["input_hash"] == case["input_hash"]
    assert out["spiff_calls"] == 1
    return out["result"]


def test_same_500_cases_spiff_vs_conductor_vs_joint():
    cases = _cases()
    config = load_workflow(FIXTURE)
    joint_spec = build_spiff_spec(config)
    timings = {"spiff": 0.0, "conductor": 0.0, "joint": 0.0}
    mismatches = []

    for case in cases:
        expected = _request(case)

        t0 = time.perf_counter()
        spiff = _spiff_only(case)
        timings["spiff"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        conductor = _conductor_only(config, case)
        timings["conductor"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        joint = _joint(joint_spec, case)
        timings["joint"] += time.perf_counter() - t0

        if not (spiff == conductor == joint == expected):
            mismatches.append((case["case_id"], spiff, conductor, joint, expected))

    print("NEXUS_COMPARE_500")
    print(f"seed={SEED} cases={CASES} mismatches={len(mismatches)}")
    for name, seconds in timings.items():
        print(f"{name}_total_seconds={seconds:.6f} {name}_mean_ms={(seconds/CASES)*1000:.6f}")

    assert not mismatches, mismatches[:5]


def test_real_powershell_tool_opens_and_returns_output():
    """Real external-tool call: start PowerShell, execute code, capture exit/output."""
    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "$PSVersionTable.PSVersion.ToString()",
        ],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    print("NEXUS_REAL_TOOL_POWERSHELL")
    print(f"exit_code={completed.returncode}")
    print(f"stdout={completed.stdout.strip()}")
    print(f"stderr={completed.stderr.strip()}")
    assert completed.returncode == 0
    assert completed.stdout.strip()
