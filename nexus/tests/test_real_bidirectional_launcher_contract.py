"""Contract for the no-install, no-deploy Windows BAT and its evidence runner."""
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from nexus.contracts import ROOT

REPO = ROOT.parent
BAT = (REPO / "TESTAR-NEXUS-REAL-BIDIRECIONAL.bat").read_text(encoding="utf-8")
PS1 = (ROOT / "windows" / "test-real-bidirectional.ps1").read_text(encoding="utf-8")


def test_existing_pc_runner_refuses_mutation_and_dirty_checkout():
    assert "test-real-bidirectional.ps1" in BAT
    assert "NEXUS_EXISTING_GIT_CHECKOUT_REQUIRED" in PS1
    assert "NEXUS_DIRTY_TREE" in PS1
    assert "verify_integrity()" in PS1
    for forbidden in ("git clone", "git pull", "git reset", "git checkout",
                      "Remove-Item", "Stop-Process", "Invoke-WebRequest",
                      "pip install", "store.promote"):
        assert forbidden.lower() not in (BAT + PS1).lower()


def test_runner_distinguishes_physical_execution_from_mocks_and_unproved_products():
    for expected in (
        "test_folha_shell_bidirectional_e2e.py",
        "test_folha_tool_composition.py",
        "test_imp001_boundary_additive.py",
        "test_native_writer_route_real.py",
        "folha_real_writer_browser.cjs",
        "test_native_languagetool_route_real.py",
        "check_media_tools.py",
        "test_procedural_learning_lab.py",
        "REAL_MCP_HEALTH_NOT_RENDER",
        "CONTRACT_CI_ONLY",
        "Mock ports reserved for isolated CI",
        "PARTIAL_NOT_PROVEN",
        "NEXUS_REAL_WRITER",
    ):
        assert expected in PS1
    assert "exit 2" in PS1


@pytest.mark.skipif(os.name != "nt", reason="PowerShell syntax proof runs on Windows CI")
def test_windows_powershell_parser_accepts_real_launcher():
    powershell = shutil.which("powershell.exe")
    assert powershell, "Required Windows parser not found"
    filename = str(Path(ROOT) / "windows" / "test-real-bidirectional.ps1").replace("'", "''")
    command = (
        "$t=$null;$e=$null;"
        "[System.Management.Automation.Language.Parser]::ParseFile('"
        + filename + "',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count -ne 0){$e|Out-String|Write-Error;exit 1}"
    )
    completed = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, text=True, timeout=20, check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_chrome_evidence_cannot_pollute_installed_source_checkout():
    assert "[string]$WorkingDirectory" in PS1
    assert "'' $folder" in PS1
    assert "Join-Path $repo 'nexus/tests/folha_real_writer_browser.cjs'" in PS1


def test_native_pc_runner_does_not_bind_mock_peers_over_live_services():
    for mocked in ("test_open_notebook_kernel_e2e.py", "test_media_tools.py"):
        assert mocked not in PS1
    assert "CONTRACT_CI_ONLY" in PS1
