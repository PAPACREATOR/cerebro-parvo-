from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest

from nexus.contracts import Blocked
from nexus.host import Host
from nexus.windows.real_acceptance import _names, _profile_endpoint


ROOT = Path(__file__).resolve().parents[2]


def test_real_acceptance_openapi_profile_discovery_is_bounded():
    spec = {
        "paths": {
            "/api/episode-profiles": {"get": {}},
            "/api/episode-profiles/{name}": {"get": {}},
            "/api/speaker-profiles": {"get": {}},
            "/api/other": {"get": {}},
        }
    }
    assert _profile_endpoint(spec, "episode-profile") == "/api/episode-profiles"
    assert _profile_endpoint(spec, "speaker-profile") == "/api/speaker-profiles"
    assert _names([{"name": "A"}, {"name": ""}, {"x": 1}]) == ["A"]


def test_real_acceptance_never_claims_external_probe_is_canonical():
    python = (ROOT / "nexus/windows/real_acceptance.py").read_text("utf-8")
    powershell = (ROOT / "nexus/windows/test-real-acceptance.ps1").read_text("utf-8")
    assert "PHYSICAL_PROBE_ONLY_NOT_HOST_PROCESS" in powershell
    assert "INCOMPLETE_UNTIL_EXTERNAL_CAPABILITIES_ENTER_HOST_CREATIVE_HUMAN_GATE" in powershell
    assert "authority" in python
    assert "UNTRUSTED" in python
    assert "does not promote" in python and "anything to Canonical" in python
    assert "from nexus.store" not in python
    assert "Store(" not in python



@pytest.mark.parametrize("process", ["music", "podcast", "avatar", "zotero", "web", "book"])
def test_external_acceptance_capabilities_cannot_be_smuggled_into_host_catalogue(tmp_path, process):
    host = Host(tmp_path)
    with pytest.raises(Blocked):
        host.start(
            {"process": process, "text": "candidate externo", "filename": "", "attachment": ""},
            host.session,
        )
    assert not list((tmp_path / "runs").iterdir())
    assert not list((tmp_path / "creative").iterdir())
    assert not list((tmp_path / "canonical").iterdir())

def test_launcher_is_thin_and_does_not_shell_out():
    source = (ROOT / "nexus/windows/NexusLauncher.cs").read_text("utf-8")
    assert ".venv" in source
    assert "-m nexus.app" in source
    assert "UseShellExecute = false" in source
    assert "cmd.exe" not in source.lower()
    assert "powershell" not in source.lower()


def test_windows_batch_entrypoints_exist_and_are_guarded():
    build = (ROOT / "CONSTRUIR-NEXUS-EXE.bat").read_text("utf-8")
    real = (ROOT / "TESTAR-NEXUS-REAL.bat").read_text("utf-8")
    assert "prepare-nexus-core.ps1" in build
    assert "build-nexus-launcher.ps1" in build
    assert "test-real-acceptance.ps1" in real
    assert "NAO entram em Canonical" in real


@pytest.mark.skipif(os.name != "nt", reason="PowerShell parser is Windows-specific here")
@pytest.mark.parametrize("relative", [
    "nexus/windows/build-nexus-launcher.ps1",
    "nexus/windows/test-real-acceptance.ps1",
])
def test_new_powershell_scripts_parse_on_real_windows(relative):
    path = ROOT / relative
    escaped = str(path).replace("'", "''")
    command = (
        "$e=$null;$t=$null;"
        f"[System.Management.Automation.Language.Parser]::ParseFile('{escaped}',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count){$e|%{$_.ToString()}|Write-Error;exit 1}"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
