import asyncio
import hashlib
import os
from pathlib import Path

import pytest

from nexus.adapters.conductor_runner import execute
from nexus.contracts import Blocked, ROOT

PS = str(Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32/WindowsPowerShell/v1.0/powershell.exe")


@pytest.mark.skipif(os.name != "nt", reason="Requires real Windows PowerShell")
def test_real_windows_tool_without_ai(tmp_path):
    source = tmp_path / "texto com espaços.txt"
    source.write_bytes(b"nexus\n")
    response = asyncio.run(execute(
        ROOT / "processes/verify.yaml",
        {"input_path": str(source), "powershell": PS, "python": os.sys.executable},
    ))
    result = response["result"]
    expected = hashlib.sha256(b"nexus\n").hexdigest()
    assert result["status"] == "PASS", result
    assert [item["value"] for item in result["evidence"]] == [expected, expected]
    assert result["ai_calls"] == 0
    assert response["trace"]["engine"] == "nexus/python-deterministic"
    assert response["trace"]["summary"]["usage"]["total_tokens"] == 0


@pytest.mark.skipif(os.name != "nt", reason="Requires real Windows PowerShell")
def test_missing_file_is_failure(tmp_path):
    response = asyncio.run(execute(
        ROOT / "processes/verify.yaml",
        {"input_path": str(tmp_path / "missing"), "powershell": PS, "python": os.sys.executable},
    ))
    assert response["result"]["status"] == "FAIL"


def test_unknown_process_is_rejected(tmp_path):
    target = tmp_path / "invalid.yaml"
    target.write_text("workflow: {}", encoding="utf-8")
    with pytest.raises(Blocked):
        asyncio.run(execute(target, {"input_path": str(tmp_path / "x"), "powershell": PS}))
