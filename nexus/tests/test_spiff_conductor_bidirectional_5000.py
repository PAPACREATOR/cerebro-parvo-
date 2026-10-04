"""5000 phased bidirectional cases: Kernel -> Spiff -> Conductor -> Kernel.

Spiff and Conductor are disposable execution layers. The Kernel owns policy,
limits, identity, persistence/recovery and all authority.
"""
import asyncio
import hashlib
import random
from pathlib import Path

import pytest
from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import Simple, WorkflowSpec
from conductor.config.loader import load_workflow
from conductor.engine.workflow import WorkflowEngine
from conductor.events import WorkflowEventEmitter

from nexus.contracts import Blocked


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "spiff_conductor_echo.yaml"
FIXTURE_SHA256 = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
MAX_PAYLOAD_BYTES = 512


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


async def conductor_once(config, request):
    events = []
    emitter = WorkflowEventEmitter()
    emitter.subscribe(lambda event: events.append(event.to_dict()))
    engine = WorkflowEngine(config, workflow_path=FIXTURE, event_emitter=emitter)
    result = await engine.run(request)
    return result, engine.get_execution_summary(), events


def build_spiff_spec(config):
    spec = WorkflowSpec("nexus-spiff-agent", addstart=True)
    agent = Simple(spec, "spiff_agent")
    spec.start.connect(agent)

    def call_conductor(workflow, task):
        kernel = workflow.data["kernel_request"]
        workflow.data["spiff_calls"] = workflow.data.get("spiff_calls", 0) + 1
        result, summary, events = asyncio.run(conductor_once(config, kernel["engine_input"]))
        workflow.data["kernel_result"] = {
            "result": result,
            "summary": summary,
            "events": events,
            "spiff_task": task.task_spec.name,
        }

    agent.completed_event.connect(call_conductor)
    return spec


def kernel_execute(spec, *, case_id, payload, direction, status, ordinal,
                   max_payload_bytes=MAX_PAYLOAD_BYTES, max_engine_calls=1):
    raw = payload.encode("utf-8")
    if len(raw) > max_payload_bytes:
        raise Blocked("Kernel payload limit exceeded.")
    if max_engine_calls != 1:
        raise Blocked("This contract permits exactly one external engine call.")

    input_hash = digest(raw)
    request = {
        "case_id": case_id,
        "input_hash": input_hash,
        "direction": direction,
        "status": status,
        "ordinal": ordinal,
    }
    workflow = Workflow(spec)
    workflow.set_data(kernel_request={"engine_input": request}, spiff_calls=0)
    workflow.run_all()

    if not workflow.is_completed():
        raise AssertionError("Spiff workflow did not complete")
    envelope = workflow.get_data("kernel_result")
    if workflow.get_data("spiff_calls") != 1:
        raise AssertionError("Kernel limit violated: unexpected Spiff call count")
    if not envelope:
        raise AssertionError("Conductor result did not return to Kernel")

    result = envelope["result"]
    reverse = {
        "case_id": result["case_id"],
        "input_hash": result["input_hash"],
        "workflow_sha256": FIXTURE_SHA256,
        "spiff_task": envelope["spiff_task"],
        "conductor_events": [event["type"] for event in envelope["events"]],
    }
    if result["case_id"] != case_id or result["input_hash"] != input_hash:
        raise AssertionError("Bidirectional identity did not close")

    return {
        "request": request,
        "result": result,
        "reverse": reverse,
        "summary": envelope["summary"],
        "spiff_calls": workflow.get_data("spiff_calls"),
    }


@pytest.fixture(scope="module")
def engines():
    config = load_workflow(FIXTURE)
    spec = build_spiff_spec(config)
    return config, spec


def test_s0_smoke_spiff_calls_conductor_and_returns_to_kernel(engines):
    _, spec = engines
    out = kernel_execute(
        spec,
        case_id="S0-0000",
        payload="nexus-spiff-conductor",
        direction="forward",
        status="PASS",
        ordinal=0,
    )
    assert out["result"]["case_id"] == "S0-0000"
    assert out["result"]["status"] == "PASS"
    assert out["reverse"]["input_hash"] == out["request"]["input_hash"]
    assert out["reverse"]["spiff_task"] == "spiff_agent"
    assert "set_completed" in out["reverse"]["conductor_events"]
    assert out["spiff_calls"] == 1


def test_s0_kernel_blocks_out_of_contract_limits_before_engines(engines):
    _, spec = engines
    with pytest.raises(Blocked):
        kernel_execute(
            spec,
            case_id="S0-LIMIT",
            payload="x" * 513,
            direction="forward",
            status="PASS",
            ordinal=0,
        )
    with pytest.raises(Blocked):
        kernel_execute(
            spec,
            case_id="S0-CALLS",
            payload="ok",
            direction="forward",
            status="PASS",
            ordinal=0,
            max_engine_calls=2,
        )


def test_s1_1000_forward_kernel_spiff_conductor(engines):
    _, spec = engines
    for i in range(1000):
        payload = f"forward:{i}:ação:日本語"
        out = kernel_execute(
            spec,
            case_id=f"S1-{i:04d}",
            payload=payload,
            direction="forward",
            status="PASS",
            ordinal=i,
        )
        assert out["result"] == {
            "case_id": f"S1-{i:04d}",
            "input_hash": digest(payload.encode("utf-8")),
            "direction": "forward",
            "status": "PASS",
            "ordinal": i,
        }


def test_s2_1000_reverse_result_to_original(engines):
    _, spec = engines
    for i in range(1000):
        payload = f"reverse:{i}:{i * 17}"
        out = kernel_execute(
            spec,
            case_id=f"S2-{i:04d}",
            payload=payload,
            direction="reverse",
            status="PASS",
            ordinal=i,
        )
        assert out["reverse"]["case_id"] == out["request"]["case_id"]
        assert out["reverse"]["input_hash"] == out["request"]["input_hash"]
        assert out["reverse"]["workflow_sha256"] == FIXTURE_SHA256
        assert "set_started" in out["reverse"]["conductor_events"]
        assert "set_completed" in out["reverse"]["conductor_events"]


def test_s3_1000_kernel_limits_and_single_dispatch(engines):
    _, spec = engines
    for i in range(1000):
        payload = ("L" * (1 + (i % 256))) + str(i)
        raw = payload.encode("utf-8")
        out = kernel_execute(
            spec,
            case_id=f"S3-{i:04d}",
            payload=payload,
            direction="bounded",
            status="PASS",
            ordinal=i,
            max_payload_bytes=len(raw),
            max_engine_calls=1,
        )
        assert out["spiff_calls"] == 1
        assert out["result"]["ordinal"] == i
        assert out["result"]["input_hash"] == digest(raw)


def test_s4_1000_status_transport_without_authority(engines):
    _, spec = engines
    states = ("PASS", "FAIL", "UNKNOWN", "BLOCKED")
    for i in range(1000):
        status = states[i % len(states)]
        payload = f"status:{status}:{i}"
        out = kernel_execute(
            spec,
            case_id=f"S4-{i:04d}",
            payload=payload,
            direction="classify",
            status=status,
            ordinal=i,
        )
        # Engines transport the classification. They do not promote, retry,
        # or reinterpret it; the Kernel remains the decision owner.
        assert out["result"]["status"] == status
        assert out["reverse"]["input_hash"] == out["request"]["input_hash"]


def test_s5_1000_seeded_joint_stress(engines):
    _, spec = engines
    rng = random.Random(20261004)
    alphabet = "abcXYZ0123 áéç_日本語_-"
    for i in range(1000):
        size = rng.randint(1, 300)
        payload = "".join(rng.choice(alphabet) for _ in range(size))
        status = ("PASS", "FAIL", "UNKNOWN", "BLOCKED")[rng.randrange(4)]
        direction = ("forward", "reverse", "bounded", "classify")[rng.randrange(4)]
        out = kernel_execute(
            spec,
            case_id=f"S5-{i:04d}",
            payload=payload,
            direction=direction,
            status=status,
            ordinal=i,
        )
        assert out["result"]["case_id"] == f"S5-{i:04d}"
        assert out["result"]["direction"] == direction
        assert out["result"]["status"] == status
        assert out["reverse"]["input_hash"] == digest(payload.encode("utf-8"))
