"""Contract for the no-install, no-deploy Windows BAT and its evidence runner."""
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
        "test_open_notebook_kernel_e2e.py",
        "check_media_tools.py",
        "test_procedural_learning_lab.py",
        "SIMULATED_PROVIDER_NOT_REAL",
        "REAL_MCP_HEALTH_NOT_RENDER",
        "PARTIAL_NOT_PROVEN",
        "NEXUS_REAL_WRITER",
    ):
        assert expected in PS1
    assert "exit 2" in PS1
