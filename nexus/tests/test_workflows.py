import asyncio
import os
import subprocess
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


@pytest.mark.skipif(os.name != "nt", reason="Requires real Windows PowerShell")
def test_real_redundant_workflow(tmp_path):
    source = tmp_path / "input.txt"
    source.write_text("Olá Nexus", encoding="utf-8")
    response = asyncio.run(execute(
        ROOT / "processes/verify.yaml",
        dict(input_path=str(source), python=sys.executable, powershell=PS),
    ))
    value = validate("result", response["result"])
    assert value["outcome"] == "agreement"
    assert value["ai_calls"] == 0
    assert response["trace"]["engine"] == "nexus/python-deterministic"
    assert response["trace"]["summary"]["usage"]["total_tokens"] == 0
    assert value["evidence"][0]["value"] == value["evidence"][1]["value"]
    assert response["trace"]["summary"]["agents_executed"] == [
        "hash_windows", "hash_python", "compare", "report"
    ]


def test_missing_tool_is_blocked(tmp_path):
    source = tmp_path / "input.txt"
    source.write_text("Nexus", encoding="utf-8")
    with pytest.raises(Blocked):
        asyncio.run(execute(
            ROOT / "processes/verify.yaml",
            {"input_path": str(source), "python": sys.executable, "powershell": str(tmp_path / "missing.exe")},
        ))


def test_timeout_is_blocked(tmp_path, monkeypatch):
    source = tmp_path / "input.txt"
    source.write_text("Nexus", encoding="utf-8")

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="powershell", timeout=15)

    monkeypatch.setattr("nexus.adapters.conductor_runner.subprocess.run", timeout)
    with pytest.raises(Blocked):
        asyncio.run(execute(
            ROOT / "processes/verify.yaml",
            {"input_path": str(source), "python": sys.executable, "powershell": "powershell.exe"},
        ))


def test_unknown_workflow(tmp_path):
    with pytest.raises(Blocked):
        asyncio.run(execute(tmp_path / "missing.yaml", {}))
