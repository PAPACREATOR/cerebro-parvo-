import asyncio
import hashlib
import json
import os
from pathlib import Path

import pytest
from conductor.config.loader import load_workflow
from conductor.engine.workflow import WorkflowEngine

ROOT = Path(__file__).resolve().parents[1]
PS = str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe")


def execute(path):
    config = load_workflow(ROOT / "processes/check.yaml")
    engine = WorkflowEngine(config, workflow_path=ROOT / "processes/check.yaml")
    # No provider and no registry: an LLM step cannot execute.
    return asyncio.run(engine.run({"input_path": str(path), "powershell": PS}))["result"]


def test_real_windows_tool_without_ai(tmp_path):
    source = tmp_path / "texto com espaços.txt"
    source.write_bytes(b"nexus\n")
    result = execute(source)
    assert result["status"] == "PASS", result
    assert result["sha256"] == hashlib.sha256(b"nexus\n").hexdigest()


def test_missing_file_is_failure(tmp_path):
    assert execute(tmp_path / "missing")["status"] == "FAIL"


def test_invalid_workflow_is_rejected(tmp_path):
    target = tmp_path / "invalid.yaml"
    target.write_text("workflow: {}", encoding="utf-8")
    with pytest.raises(Exception):
        load_workflow(target)
