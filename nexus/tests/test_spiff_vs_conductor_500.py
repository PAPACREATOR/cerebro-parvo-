"""A/B/C Lab: same 500 seeded cases through Spiff-only, Conductor-only and Spiff->Conductor.

This is evidence only. It does not alter Kernel authority, Creative/Canonical or Human Gate.
"""
import asyncio
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytest.importorskip("SpiffWorkflow", reason="Spiff is an optional Lab executor")
from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import Simple, WorkflowSpec
from conductor.config.loader import load_workflow
from conductor.engine.workflow import WorkflowEngine

from nexus.tests.test_spiff_conductor_bidirectional_5000 import build_spiff_spec, kernel_execute
from nexus.adapters.tools import hash_python, compare as compare_hashes, report as build_report

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


def _run_real_tool(label, command, *, timeout=20):
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    print(f"NEXUS_REAL_TOOL {label}")
    print(f"command={command}")
    print(f"exit_code={completed.returncode}")
    print(f"stdout={completed.stdout.strip()}")
    print(f"stderr={completed.stderr.strip()}")
    return completed


def test_real_windows_toolchain_multiple_calls():
    probes = [
        ("powershell", ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "$PSVersionTable.PSVersion.ToString()"]),
        ("cmd", ["cmd.exe", "/d", "/c", "ver"]),
        ("git", ["git.exe", "--version"]),
        ("python-child", [sys.executable, "-c", "import sys; print(sys.version); print('NEXUS_CHILD_OK')"]),
    ]
    for label, command in probes:
        completed = _run_real_tool(label, command)
        assert completed.returncode == 0, (label, completed.stderr)
        assert completed.stdout.strip(), label


def test_real_optional_external_tool_discovery():
    # Optional desktop/runtime capabilities: absence is recorded as BLOCKED,
    # never misreported as an integration PASS.
    candidates = {
        "libreoffice": ["soffice.exe", "--headless", "--version"],
        "java": ["java.exe", "-version"],
        "zotero": ["zotero.exe", "--version"],
    }
    for label, command in candidates.items():
        locator = subprocess.run(
            ["where.exe", command[0]],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if locator.returncode != 0:
            print(f"NEXUS_REAL_TOOL {label} status=BLOCKED reason=TOOL_UNAVAILABLE")
            continue
        completed = _run_real_tool(label, command)
        # Some tools (notably java -version) write version info to stderr.
        assert completed.returncode == 0, (label, completed.stderr)
        assert completed.stdout.strip() or completed.stderr.strip(), label


CHECK_FLOW = ROOT / "processes" / "check.yaml"
PS_EXE = str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe")


def _ps_hash_direct(path):
    script = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$p = [Console]::In.ReadToEnd().TrimEnd([char]10, [char]13)
try {
  $algorithm = [System.Security.Cryptography.SHA256]::Create()
  try { $hash = [BitConverter]::ToString($algorithm.ComputeHash([System.IO.File]::ReadAllBytes($p))).Replace('-', '').ToLowerInvariant() }
  finally { $algorithm.Dispose() }
  [Console]::Out.WriteLine('{"status":"PASS","sha256":"' + $hash + '","capability":"windows.dotnet-sha256"}')
} catch {
  [Console]::Out.WriteLine('{"status":"FAIL","sha256":null,"capability":"windows.dotnet-sha256"}')
}
"""
    completed = subprocess.run(
        [PS_EXE, "-NoProfile", "-NonInteractive", "-Command", script],
        input=str(path),
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout.strip().splitlines()[-1])


def _spiff_real_tool(path):
    spec = WorkflowSpec("nexus-spiff-real-tool", addstart=True)
    task = Simple(spec, "powershell_hash")
    spec.start.connect(task)

    def invoke(workflow, _task):
        workflow.data["result"] = _ps_hash_direct(workflow.data["path"])
        workflow.data["tool_calls"] = workflow.data.get("tool_calls", 0) + 1

    task.completed_event.connect(invoke)
    workflow = Workflow(spec)
    workflow.set_data(path=str(path), tool_calls=0)
    workflow.run_all()
    assert workflow.is_completed()
    assert workflow.get_data("tool_calls") == 1
    return workflow.get_data("result")


async def _conductor_real_tool_async(path):
    config = load_workflow(CHECK_FLOW)
    engine = WorkflowEngine(config, workflow_path=CHECK_FLOW)
    return await engine.run({"input_path": str(path), "powershell": PS_EXE})


def _conductor_real_tool(path):
    return asyncio.run(_conductor_real_tool_async(path))["result"]


def _joint_real_tool(path):
    config = load_workflow(CHECK_FLOW)
    spec = WorkflowSpec("nexus-spiff-conductor-real-tool", addstart=True)
    task = Simple(spec, "spiff_dispatch_conductor")
    spec.start.connect(task)

    def invoke(workflow, _task):
        engine = WorkflowEngine(config, workflow_path=CHECK_FLOW)
        envelope = asyncio.run(engine.run({"input_path": workflow.data["path"], "powershell": PS_EXE}))
        workflow.data["result"] = envelope["result"]
        workflow.data["spiff_calls"] = workflow.data.get("spiff_calls", 0) + 1

    task.completed_event.connect(invoke)
    workflow = Workflow(spec)
    workflow.set_data(path=str(path), spiff_calls=0)
    workflow.run_all()
    assert workflow.is_completed()
    assert workflow.get_data("spiff_calls") == 1
    return workflow.get_data("result")


def _real_tool_cases(tmp_path):
    cases = []
    fixed = [
        ("empty.bin", b""),
        ("one-byte.bin", b"x"),
        ("ascii.txt", b"Nexus real PowerShell tool\n"),
        ("unicode.txt", "ação 日本語 café\n".encode("utf-8")),
        ("nulls.bin", b"\x00\x01\x00\xffNEXUS"),
        ("spaces name.txt", b"spaces"),
        ("acentuação çã.txt", "ficheiro com nome unicode".encode("utf-8")),
        ("4k.bin", bytes(range(256)) * 16),
    ]
    for name, raw in fixed:
        path = tmp_path / name
        path.write_bytes(raw)
        cases.append(path)
    rng = random.Random(SEED)
    for i in range(16):
        raw = bytes(rng.randrange(256) for _ in range(1 + rng.randrange(2048)))
        path = tmp_path / f"random-{i:02d}.bin"
        path.write_bytes(raw)
        cases.append(path)
    return cases


def test_real_powershell_same_cases_spiff_conductor_joint(tmp_path):
    cases = _real_tool_cases(tmp_path)
    totals = {"spiff": 0.0, "conductor": 0.0, "joint": 0.0}
    mismatches = []

    for path in cases:
        expected_hash = hashlib.sha256(path.read_bytes()).hexdigest()

        t0 = time.perf_counter()
        spiff = _spiff_real_tool(path)
        totals["spiff"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        conductor = _conductor_real_tool(path)
        totals["conductor"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        joint = _joint_real_tool(path)
        totals["joint"] += time.perf_counter() - t0

        values = (spiff, conductor, joint)
        if not all(v.get("status") == "PASS" and v.get("sha256") == expected_hash for v in values):
            mismatches.append((path.name, spiff, conductor, joint, expected_hash))

    print("NEXUS_REAL_TOOL_COMPARISON")
    print("| Path | Cases | Result | Total s | Mean ms | Real PowerShell calls |")
    print("|---|---:|---|---:|---:|---:|")
    for name in ("spiff", "conductor", "joint"):
        result = "PASS" if not mismatches else "FAIL"
        print(f"| {name} | {len(cases)} | {result} | {totals[name]:.6f} | {(totals[name]/len(cases))*1000:.3f} | {len(cases)} |")
    print(f"mismatches={len(mismatches)}")
    assert not mismatches, mismatches[:5]


VERIFY_FLOW = ROOT / "processes" / "verify.yaml"


def _spiff_complex_verify(path):
    spec = WorkflowSpec("nexus-spiff-complex-verify", addstart=True)
    ps_task = Simple(spec, "hash_windows")
    py_task = Simple(spec, "hash_python")
    compare_task = Simple(spec, "compare")
    report_task = Simple(spec, "report")
    spec.start.connect(ps_task)
    ps_task.connect(py_task)
    py_task.connect(compare_task)
    compare_task.connect(report_task)

    def do_ps(workflow, _task):
        workflow.data["a"] = _ps_hash_direct(workflow.data["path"])
        workflow.data["calls"] = workflow.data.get("calls", 0) + 1

    def do_py(workflow, _task):
        workflow.data["b"] = hash_python(workflow.data["path"])
        workflow.data["calls"] = workflow.data.get("calls", 0) + 1

    def do_compare(workflow, _task):
        workflow.data["comparison"] = compare_hashes(workflow.data["a"], workflow.data["b"])

    def do_report(workflow, _task):
        policy = {"agreement":"PASS","conflict":"UNKNOWN","unknown":"UNKNOWN","failure":"FAIL"}
        outcome = workflow.data["comparison"]["outcome"]
        workflow.data["result"] = build_report({
            "comparison": workflow.data["comparison"],
            "status": policy[outcome],
        })

    ps_task.completed_event.connect(do_ps)
    py_task.completed_event.connect(do_py)
    compare_task.completed_event.connect(do_compare)
    report_task.completed_event.connect(do_report)

    workflow = Workflow(spec)
    workflow.set_data(path=str(path), calls=0)
    workflow.run_all()
    assert workflow.is_completed()
    assert workflow.get_data("calls") == 2
    return workflow.get_data("result")


async def _conductor_complex_async(path):
    config = load_workflow(VERIFY_FLOW)
    engine = WorkflowEngine(config, workflow_path=VERIFY_FLOW)
    envelope = await engine.run({
        "input_path": str(path),
        "powershell": PS_EXE,
        "python": sys.executable,
    })
    return envelope["result"], engine.get_execution_summary()


def _conductor_complex_verify(path):
    return asyncio.run(_conductor_complex_async(path))


def _joint_complex_verify(path):
    config = load_workflow(VERIFY_FLOW)
    spec = WorkflowSpec("nexus-spiff-conductor-complex", addstart=True)
    task = Simple(spec, "dispatch_conductor_verify")
    spec.start.connect(task)

    def invoke(workflow, _task):
        engine = WorkflowEngine(config, workflow_path=VERIFY_FLOW)
        envelope = asyncio.run(engine.run({
            "input_path": workflow.data["path"],
            "powershell": PS_EXE,
            "python": sys.executable,
        }))
        workflow.data["result"] = envelope["result"]
        workflow.data["summary"] = engine.get_execution_summary()
        workflow.data["spiff_calls"] = workflow.data.get("spiff_calls", 0) + 1

    task.completed_event.connect(invoke)
    workflow = Workflow(spec)
    workflow.set_data(path=str(path), spiff_calls=0)
    workflow.run_all()
    assert workflow.is_completed()
    assert workflow.get_data("spiff_calls") == 1
    return workflow.get_data("result"), workflow.get_data("summary")


def _assert_reverse_to_source(result, path):
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    assert result["status"] == "PASS"
    assert result["outcome"] == "agreement"
    assert result["ai_calls"] == 0
    values = [item["value"] for item in result["evidence"]]
    assert values == [expected, expected]
    return expected


def test_complex_bidirectional_verify_three_paths(tmp_path):
    cases = _real_tool_cases(tmp_path)[:12]
    totals = {"spiff": 0.0, "conductor": 0.0, "joint": 0.0}
    mismatches = []

    for path in cases:
        t0 = time.perf_counter()
        spiff = _spiff_complex_verify(path)
        totals["spiff"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        conductor, conductor_summary = _conductor_complex_verify(path)
        totals["conductor"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        joint, joint_summary = _joint_complex_verify(path)
        totals["joint"] += time.perf_counter() - t0

        expected = _assert_reverse_to_source(spiff, path)
        _assert_reverse_to_source(conductor, path)
        _assert_reverse_to_source(joint, path)

        # Same semantic result and same reverse evidence. Capability labels are
        # intentionally preserved and therefore compared explicitly as data.
        if not (spiff == conductor == joint):
            mismatches.append((path.name, spiff, conductor, joint))

        for summary in (conductor_summary, joint_summary):
            executed = summary["agents_executed"]
            assert "hash_windows" in executed
            assert "hash_python" in executed
            assert "compare" in executed
            assert "report" in executed

        # reverse closure: output evidence -> original bytes
        assert expected == hashlib.sha256(path.read_bytes()).hexdigest()

    print("NEXUS_COMPLEX_BIDIRECTIONAL_THREE_PATHS")
    print("| Path | Cases | Result | Total s | Mean ms | Reverse to source |")
    print("|---|---:|---|---:|---:|---|")
    for name in ("spiff", "conductor", "joint"):
        result = "PASS" if not mismatches else "FAIL"
        print(f"| {name} | {len(cases)} | {result} | {totals[name]:.6f} | {(totals[name]/len(cases))*1000:.3f} | PASS |")
    print(f"complex_mismatches={len(mismatches)}")
    assert not mismatches, mismatches[:3]


def _normalized_open_notebook_result(value):
    value = dict(value)
    value.pop("request_id", None)
    return value


async def _python_mcp_open_notebook_search_async(query, detail="summary", limit=20):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "open_notebook_mcp.server"],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            assert "search_capabilities" in names
            result = await session.call_tool(
                "search_capabilities",
                arguments={"query": query, "detail": detail, "limit": limit},
            )
            assert not result.isError
            value = result.structured_content
            if value is None:
                texts = [getattr(item, "text", None) for item in result.content]
                texts = [item for item in texts if item]
                assert texts, result
                value = json.loads(texts[0])
            return _normalized_open_notebook_result(value)


def _python_mcp_open_notebook_search(query, detail="summary", limit=20):
    return asyncio.run(_python_mcp_open_notebook_search_async(query, detail, limit))


def _spiff_mcp_open_notebook_search(query, detail="summary", limit=20):
    spec = WorkflowSpec("nexus-spiff-python-mcp-open-notebook", addstart=True)
    task = Simple(spec, "open_notebook_mcp")
    spec.start.connect(task)

    def invoke(workflow, _task):
        workflow.data["result"] = _python_mcp_open_notebook_search(
            workflow.data["query"], workflow.data["detail"], workflow.data["limit"]
        )
        workflow.data["calls"] = workflow.data.get("calls", 0) + 1

    task.completed_event.connect(invoke)
    workflow = Workflow(spec)
    workflow.set_data(query=query, detail=detail, limit=limit, calls=0)
    workflow.run_all()
    assert workflow.is_completed()
    assert workflow.get_data("calls") == 1
    return workflow.get_data("result")


def _write_conductor_open_notebook_mcp_flow(path):
    path.write_text(
        """workflow:
  name: nexus-open-notebook-mcp-compare
  version: "1.0.0"
  entry_point: search
  runtime:
    provider: copilot
    mcp_servers:
      open-notebook:
        type: stdio
        command: python
        args: ["-m", "open_notebook_mcp.server"]
        tools: ["search_capabilities"]
  limits:
    max_iterations: 3
    timeout_seconds: 45
agents:
  - name: search
    type: mcp
    server: open-notebook
    tool: search_capabilities
    arguments:
      query: "{{ workflow.input.query }}"
      detail: "{{ workflow.input.detail }}"
      limit: "{{ workflow.input.limit }}"
    timeout: 30
    routes:
      - to: $end
output:
  done: true
""",
        encoding="utf-8",
    )


async def _conductor_mcp_open_notebook_async(flow, query, detail="summary", limit=20):
    config = load_workflow(flow)
    engine = WorkflowEngine(config, workflow_path=flow)
    await engine.run({"query": query, "detail": detail, "limit": limit})
    value = engine.context.agent_outputs["search"]
    # Conductor's MCP envelope merges structured keys onto the output.
    semantic = {
        key: value[key]
        for key in ("query", "detail", "count", "matches", "hint")
        if key in value
    }
    return _normalized_open_notebook_result(semantic), engine.get_execution_summary()


def _conductor_mcp_open_notebook_search(flow, query, detail="summary", limit=20):
    return asyncio.run(_conductor_mcp_open_notebook_async(flow, query, detail, limit))


def test_minimal_python_mcp_vs_spiff_vs_conductor_open_notebook(tmp_path):
    queries = [
        "", "notebook", "source", "notes", "search", "vector",
        "question", "chat", "models", "settings", "create", "delete",
    ]
    flow = tmp_path / "open-notebook-mcp-conductor.yaml"
    _write_conductor_open_notebook_mcp_flow(flow)
    totals = {"python-mcp": 0.0, "spiff+mcp": 0.0, "conductor+mcp": 0.0}
    mismatches = []

    for query in queries:
        t0 = time.perf_counter()
        pure = _python_mcp_open_notebook_search(query)
        totals["python-mcp"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        spiff = _spiff_mcp_open_notebook_search(query)
        totals["spiff+mcp"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        conductor, summary = _conductor_mcp_open_notebook_search(flow, query)
        totals["conductor+mcp"] += time.perf_counter() - t0

        if not (pure == spiff == conductor):
            mismatches.append((query, pure, spiff, conductor))

        assert summary["usage"]["total_tokens"] == 0
        assert "search" in summary["agents_executed"]

    print("NEXUS_MINIMAL_MCP_OPEN_NOTEBOOK")
    print("| Stack | Queries | Result | Total s | Mean ms | LLM tokens |")
    print("|---|---:|---|---:|---:|---:|")
    for name in ("python-mcp", "spiff+mcp", "conductor+mcp"):
        result = "PASS" if not mismatches else "FAIL"
        print(f"| {name} | {len(queries)} | {result} | {totals[name]:.6f} | {(totals[name]/len(queries))*1000:.3f} | 0 |")
    print(f"mcp_semantic_mismatches={len(mismatches)}")
    assert not mismatches, mismatches[:3]


def test_minimal_mcp_failure_and_repeatability():
    # Repeat the same deterministic tool request three times. request_id is
    # transport metadata and is deliberately excluded from semantic equality.
    values = [_python_mcp_open_notebook_search("podcast", detail="summary", limit=50) for _ in range(3)]
    assert values[0] == values[1] == values[2]
    assert values[0]["query"] == "podcast"
    # Current OpenNotebook MCP has no podcast capability exposed in its 39-tool
    # index, so this must be an explicit empty result rather than an invented tool.
    assert values[0]["count"] == 0


def _dependency_closure(root_names):
    import importlib.metadata as md
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name

    dists = {canonicalize_name(d.metadata["Name"]): d for d in md.distributions() if d.metadata.get("Name")}
    seen = set()
    pending = [canonicalize_name(name) for name in root_names]
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        dist = dists.get(name)
        assert dist is not None, (name, sorted(dists)[:20])
        seen.add(name)
        for raw in dist.requires or []:
            req = Requirement(raw)
            if req.marker is not None and not req.marker.evaluate({"extra": ""}):
                continue
            dep = canonicalize_name(req.name)
            if dep in dists and dep not in seen:
                pending.append(dep)
    total = 0
    for name in seen:
        dist = dists[name]
        for item in dist.files or []:
            try:
                target = dist.locate_file(item)
                if target.is_file():
                    total += target.stat().st_size
            except OSError:
                pass
    return seen, total


def test_dependency_footprint_python_mcp_spiff_conductor():
    stacks = {
        "python-mcp": ["open-notebook-mcp", "mcp"],
        "spiff+mcp": ["open-notebook-mcp", "mcp", "SpiffWorkflow"],
        "conductor+mcp": ["open-notebook-mcp", "mcp", "conductor-cli"],
    }
    values = {}
    print("NEXUS_DEPENDENCY_FOOTPRINT")
    print("| Stack | Distribution closure | Installed MiB |")
    print("|---|---:|---:|")
    for name, roots in stacks.items():
        closure, size = _dependency_closure(roots)
        values[name] = (closure, size)
        print(f"| {name} | {len(closure)} | {size/(1024*1024):.2f} |")
    assert values["python-mcp"][0].issubset(values["spiff+mcp"][0])
    assert values["python-mcp"][0].issubset(values["conductor+mcp"][0])
    assert values["python-mcp"][1] <= values["spiff+mcp"][1]
    assert values["python-mcp"][1] <= values["conductor+mcp"][1]
