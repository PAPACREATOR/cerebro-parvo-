"""Final install/test BAT contracts.

These are launchers only. They must not contain passwords, create Windows
accounts, bypass the human install gate, or write/promote Canonical.
"""
from pathlib import Path

from nexus.contracts import ROOT


REPO = ROOT.parent
INSTALL_BAT = (REPO / "INSTALAR-NEXUS-COMPLETO.bat").read_text(encoding="utf-8")
TEST_BAT = (REPO / "TESTAR-NEXUS-POS-INSTALACAO.bat").read_text(encoding="utf-8")
POST = (ROOT / "windows" / "test-post-install.ps1").read_text(encoding="utf-8")


def test_install_bat_is_explicit_and_password_free():
    assert "install-nexus-complete.ps1" in INSTALL_BAT
    assert "-AuthorizeInstall" in INSTALL_BAT
    assert "C:\\Nexus-Tools" in INSTALL_BAT
    for forbidden in ("New-LocalUser", "Add-LocalGroupMember", "Read-Host", "-Password", "password="):
        assert forbidden not in INSTALL_BAT
    assert "nao cria contas Windows Nexus/NexusTool" in INSTALL_BAT


def test_post_install_bat_only_calls_bounded_acceptance():
    assert "test-post-install.ps1" in TEST_BAT
    assert "complete-install-report.json" in TEST_BAT
    assert "post-install-acceptance-report.json" in TEST_BAT
    assert "store.promote" not in TEST_BAT.lower()
    assert "\\canonical\\" not in TEST_BAT.lower()
    assert "nao promove nem escreve diretamente no canonical" in TEST_BAT.lower()


def test_post_install_acceptance_runs_exact_stress_and_security_gates():
    required = (
        "test_product_flows_5000.py",
        "test_product_system_50000.py",
        "test_product_themes_canonical_200k.py",
        "test_system_varied_200k.py",
        "test_bidirectional_50000.py",
        "test_authority_10000.py",
        "test_native_boundary.py",
        "test_confinement_gate.py",
        "NEXUS_RUN_50K",
        "CreateAppContainerProfile",
        "AssignProcessToJobObject",
        "qwen3:4b",
        "nomic-embed-text",
        "torch.cuda.is_available",
        "MoneyPrinterTurbo",
    )
    for token in required:
        assert token.lower() in POST.lower()


def test_post_install_acceptance_never_promotes_or_creates_accounts():
    for forbidden in (
        "store.promote",
        ".promote(",
        "New-LocalUser",
        "Add-LocalGroupMember",
        "Read-Host",
    ):
        assert forbidden not in POST
    assert "NEXUS_REUSABLE_TOOL_IDENTITY_FOUND" in POST
    assert "LogonUser" in POST and "CreateProcessAsUser" in POST
    assert "legacy_accounts_present" in POST
    assert "per-task AppContainer" in POST
