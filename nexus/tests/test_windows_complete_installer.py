from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = (ROOT / "windows" / "install-nexus-complete.ps1").read_text(encoding="utf-8")
MEDIA = (ROOT / "windows" / "install-media-tools.ps1").read_text(encoding="utf-8")
AVATAR = (ROOT / "lab" / "open_notebook_avatar" / "install-windows.ps1").read_text(encoding="utf-8")
MODELS = (ROOT / "lab" / "open_notebook_avatar" / "provision_models.py").read_text(encoding="utf-8")
ROUTER = (ROOT / "lab" / "open_notebook_avatar" / "install_router.py").read_text(encoding="utf-8")
LAUNCHER = (ROOT / "windows" / "nexus-launcher.py").read_text(encoding="utf-8")


def test_complete_installer_requires_explicit_human_authorization():
    assert "[switch]$AuthorizeInstall" in MASTER
    assert "if (-not $AuthorizeInstall)" in MASTER
    assert "NEXUS_INSTALL_AUTHORIZATION_REQUIRED" in MASTER
    assert MASTER.index("if (-not $AuthorizeInstall)") < MASTER.index("Ensure-WingetPackage 'Git.Git'")


def test_nested_installers_remain_fail_closed_without_authorization():
    for script in (MEDIA, AVATAR):
        assert "[switch]$AuthorizeInstall" in script
        assert "if (-not $AuthorizeInstall)" in script
        assert "NEXUS_INSTALL_AUTHORIZATION_REQUIRED" in script
    assert "-AuthorizeInstall" in MASTER


def test_model_download_is_authorized_explicitly_not_by_ambient_state():
    assert "authorize_install=False" in MODELS
    assert "authorize_install is not True" in MODELS
    assert '--authorize-install' in MODELS
    assert "'--authorize-install'" in AVATAR


def test_installer_pins_the_external_source_trees_and_binary_hashes():
    expected = (
        "315d5255af2a5132aada41c94d5c3c5dc8e837aa",
        "993994f7984bf3fe9655b267448328cf66fccb42",
        "ca1e85fe9430179831e6bc6be790c332190a3866",
        "dfdcbab685e57677014f05a3309b48cc87383167",
        "55c7e05ee2b68ec0d8b86c4b588e9b9807f257af8c15c05d17074514c64d8c91",
        "53600506b399bb5ffe1e4c8dec794fd378212f14aaf38ccef9b6f89314d11631",
    )
    joined = MASTER + MEDIA
    for value in expected:
        assert value in joined


def test_installer_uses_current_zotero_and_expected_windows_dependencies():
    for package in (
        "Git.Git", "Python.Python.3.12", "OpenJS.NodeJS.LTS",
        "Microsoft.OpenJDK.17", "TheDocumentFoundation.LibreOffice",
        "DigitalScholar.Zotero", "Gyan.FFmpeg", "astral-sh.uv", "Ollama.Ollama",
    ):
        assert package in MASTER


def test_installer_prepares_local_models_needed_for_later_physical_acceptance():
    for value in (
        "qwen3:4b", "nomic-embed-text",
        "speaches-ai/Kokoro-82M-v1.0-ONNX",
        "acestep-v15-turbo", "wav2lip.pth", "s3fd.pth",
    ):
        assert value in MASTER or value in AVATAR or value in MODELS


def test_installer_does_not_claim_unconfigured_open_notebook_or_forge_bindings():
    assert "PASS_WITH_EXPLICIT_PENDING_BINDINGS" in MASTER
    assert "OPEN_NOTEBOOK_MODEL_AND_TRANSFORMATION_BINDING" in MASTER
    assert "FORGE_IMAGE_CHECKPOINT_SELECTION" in MASTER
    assert "model='NOT_SELECTED'" in MASTER


def test_installer_never_writes_or_deletes_nexus_vaults():
    lowered = MASTER.lower()
    for forbidden in (
        "join-path $runtime 'canonical'",
        "join-path $runtime 'creative'",
        "store.promote",
        "shutil.rmtree",
        "reset --hard",
        "git clean",
    ):
        assert forbidden not in lowered


def test_launcher_is_thin_and_uses_validated_external_python_and_git():
    assert '"python"' in LAUNCHER
    assert '"git"' in LAUNCHER
    assert '"expected_origin"' in LAUNCHER
    assert '"-m", "nexus.app"' in LAUNCHER
    assert "PyInstaller" not in LAUNCHER
    assert "nexus.host" not in LAUNCHER
    assert "nexus.store" not in LAUNCHER


def test_avatar_router_matches_the_pinned_open_notebook_version():
    assert 'version != "1.15.0"' in ROUTER
    assert "Open Notebook 1.15.0" in ROUTER
    assert "app.include_router(podcasts.router" in ROUTER
