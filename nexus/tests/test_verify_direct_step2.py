"""Step 2: verify direct Python vs legacy Conductor, with real Windows tooling."""
import asyncio
import hashlib
import os
import random
import sys
from pathlib import Path

import pytest

from nexus.adapters.conductor_runner import execute as conductor_execute
from nexus.adapters.verify_direct import execute as direct_execute
from nexus.contracts import ROOT, Blocked

PS = str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe")


def legacy(path):
    return asyncio.run(conductor_execute(
        ROOT / "processes/verify.yaml",
        {"input_path": str(path), "python": sys.executable, "powershell": PS},
    ))


def semantic(envelope):
    return envelope["result"]


@pytest.mark.skipif(os.name != "nt", reason="Real PowerShell/.NET comparison requires Windows")
def test_100_real_inputs_exact_semantic_equivalence_and_reverse_hash(tmp_path):
    rng = random.Random(20261004)
    for i in range(100):
        if i == 0:
            raw = b""
        elif i == 1:
            raw = b"x" * (2 * 1024 * 1024)
        elif i % 3 == 0:
            raw = ("Ação memória 日本語 ç linha " + str(i) + "\n").encode("utf-8")
        else:
            raw = bytes(rng.randrange(256) for _ in range(1 + (i * 7919) % 65536))
        name = f"{i:03d}-ação 日本語 & $ ' %.bin"
        path = tmp_path / name
        path.write_bytes(raw)
        expected = hashlib.sha256(raw).hexdigest()

        direct = direct_execute(path, powershell=PS)
        old = legacy(path)

        assert semantic(direct) == semantic(old), i
        assert direct["result"]["status"] == "PASS"
        assert direct["result"]["outcome"] == "agreement"
        assert direct["result"]["ai_calls"] == 0
        assert [item["value"] for item in direct["result"]["evidence"]] == [expected, expected]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        assert direct["trace"]["summary"]["usage"]["total_tokens"] == 0


@pytest.mark.skipif(os.name != "nt", reason="Real PowerShell/.NET comparison requires Windows")
def test_missing_file_same_failure_semantics(tmp_path):
    path = tmp_path / "não existe.bin"
    direct = direct_execute(path, powershell=PS)
    old = legacy(path)
    assert semantic(direct) == semantic(old)
    assert direct["result"]["status"] == "FAIL"
    assert direct["result"]["outcome"] == "failure"
    assert [item["status"] for item in direct["result"]["evidence"]] == ["FAIL", "FAIL"]


def test_missing_powershell_is_explicitly_blocked(tmp_path):
    path = tmp_path / "input.txt"
    path.write_text("nexus", encoding="utf-8")
    with pytest.raises(Blocked, match="indisponível"):
        direct_execute(path, powershell=str(tmp_path / "missing-powershell.exe"))


@pytest.mark.skipif(os.name != "nt", reason="Real PowerShell required")
def test_timeout_is_explicitly_blocked(tmp_path):
    path = tmp_path / "input.txt"
    path.write_text("nexus", encoding="utf-8")
    with pytest.raises(Blocked, match="excedeu"):
        direct_execute(path, powershell=PS, timeout=0.000001)


@pytest.mark.skipif(os.name != "nt", reason="Real PowerShell required")
def test_repeatability_same_bytes_same_result(tmp_path):
    path = tmp_path / "ação.txt"
    path.write_bytes("conteúdo fixo 日本語".encode("utf-8"))
    first = direct_execute(path, powershell=PS)["result"]
    for _ in range(20):
        assert direct_execute(path, powershell=PS)["result"] == first
