import asyncio
import json
import sys
from pathlib import Path
import pytest
from nexus.adapters.conductor_runner import execute
from nexus.adapters.tools import compare, report
from nexus.contracts import ROOT, validate, Blocked
from nexus.tests.test_conductor import PS


@pytest.mark.parametrize("left,right,outcome,status", [
    (("PASS", "abc"), ("PASS", "abc"), "agreement", "PASS"),
    (("PASS", "abc"), ("PASS", "def"), "conflict", "UNKNOWN"),
    (("UNKNOWN", None), ("PASS", "abc"), "unknown", "UNKNOWN"),
    (("FAIL", None), ("PASS", "abc"), "failure", "FAIL"),
])
def test_comparison_preserves_both_sides(left, right, outcome, status):
    a = dict(status=left[0], sha256=left[1], capability="A")
    b = dict(status=right[0], sha256=right[1], capability="B")
    compared = compare(a, b)
    assert compared == dict(outcome=outcome, a=a, b=b)
    value = report(dict(comparison=compared, status=status))
    validate("result", value)
    assert [v["value"] for v in value["evidence"]] == [left[1], right[1]]


def test_real_redundant_workflow(tmp_path, monkeypatch):
    from conductor.engine.workflow import WorkflowEngine
    async def forbidden(*args, **kwargs):
        pytest.fail("Tentativa de obter provider de IA")
    monkeypatch.setattr(WorkflowEngine, "_get_provider_for_agent", forbidden)
    source = tmp_path / "input.txt"
    source.write_text("Olá Nexus", encoding="utf-8")
    response = asyncio.run(execute(ROOT / "processes/verify.yaml",
        dict(input_path=str(source), python=sys.executable, powershell=PS)))
    value = validate("result", response["result"])
    assert value["outcome"] == "agreement"
    assert value["ai_calls"] == 0
    assert response["trace"]["summary"]["usage"]["total_tokens"] == 0
    assert value["evidence"][0]["value"] == value["evidence"][1]["value"]
    assert "hash_windows" in response["trace"]["summary"]["agents_executed"]
    assert "hash_python" in response["trace"]["summary"]["agents_executed"]


def test_failure_paths_through_real_engine(tmp_path):
    # Small artificial workflow uses the real engine to verify failure semantics.
    from ruamel.yaml import YAML
    cases = [
        (str(tmp_path / "no-such-tool.exe"), [], 1),
        (sys.executable, ["-c", "import time; time.sleep(5)"], 1),
    ]
    for index, (command, args, timeout) in enumerate(cases):
        path = tmp_path / (str(index) + ".yaml")
        config = {"workflow": {"name": "failure-test", "entry_point": "tool"},
            "agents": [{"name": "tool", "type": "script", "command": command,
                "args": args, "timeout": timeout, "routes": [{"to": "$end"}]}],
            "output": {"result": "{{ tool.output.stdout }}"}}
        with path.open("w", encoding="utf-8") as file:
            YAML().dump(config, file)
        with pytest.raises(Exception):
            asyncio.run(execute(path, {}))


def test_unknown_workflow(tmp_path):
    with pytest.raises(Exception):
        asyncio.run(execute(tmp_path / "missing.yaml", {}))
