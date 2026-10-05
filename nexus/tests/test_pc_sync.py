from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "windows" / "sync-nexus-pc.ps1").read_text(encoding="utf-8")


def test_pc_sync_uses_single_checkout_and_fast_forward_only():
    assert "git reset --hard" not in SCRIPT.lower()
    assert "'merge','--ff-only'" in SCRIPT
    assert "single_checkout" in SCRIPT
    assert "Nexus-old" not in SCRIPT
    assert "backup-nexus" not in SCRIPT


def test_pc_sync_refuses_dirty_tree():
    assert "status --porcelain" in SCRIPT
    assert "árvore Git tem alterações locais" in SCRIPT


def test_pc_sync_targets_official_repository_and_branch():
    assert "PAPACREATOR/cerebro-parvo-" in SCRIPT
    assert "lab-open-notebook-avatar-20261004" in SCRIPT
    assert "origin/$Branch" in SCRIPT


def test_pc_sync_runs_full_nexus_validation_before_media():
    nexus = SCRIPT.index("-Suite all")
    install = SCRIPT.index("install-media-tools.ps1")
    assert nexus < install


def test_pc_sync_uses_external_tools_and_physical_health_gate():
    assert "C:\\Nexus-Tools" in SCRIPT
    assert "Start-ACE-Step-Nexus.cmd" in SCRIPT
    assert "Start-Forge-Nexus.cmd" in SCRIPT
    assert "check-media-tools.ps1" in SCRIPT
    assert "-WaitSeconds 180" in SCRIPT


def test_pc_sync_writes_one_bootstrap_report():
    assert "pc-bootstrap.json" in SCRIPT
    assert "media-health.json" in SCRIPT
    assert "NEXUS PC = PASS" in SCRIPT
