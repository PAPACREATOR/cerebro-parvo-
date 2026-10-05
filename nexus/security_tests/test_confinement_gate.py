"""Security acceptance gate, not an expected-failure regression test.

Simulates a compromised allowed worker at the actual Host subprocess launch.
Only its executable payload is substituted; Host cwd/env/identity/flags remain.
Every target is a disposable canary. No real Kernel/user/Windows file is touched.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from nexus.host import Host, ROOT


AREAS = ("kernel", "creative", "canonical", "outside-install")
ACTIONS = ("overwrite", "create", "delete", "rename", "mkdir")
CASES = [(area, action) for area in AREAS for action in ACTIONS]
CASES += [(area, "read") for area in ("creative", "canonical")]


@pytest.fixture(scope="module")
def observations(tmp_path_factory):
    # This gate is deliberately Windows-only: never report Linux as Windows proof.
    assert os.name == "nt", "Windows confinement gate NOT RUN on this OS"
    root = tmp_path_factory.mktemp("nexus-confinement")
    (root / "TEST-AREA-ONLY").write_text("nexus-disposable-confinement-v1")
    install = root / "installation"
    host = Host(install / "data")
    run_id = host.store.create(dict(process="verify", text="synthetic", filename="", attachment=""))
    run_dir = host.store.path("runs", run_id)
    areas = {
        "kernel": install / "kernel-canaries",
        "creative": host.store.root / "creative",
        "canonical": host.store.root / "canonical",
        "outside-install": root / "user-profile-canaries",
    }
    manifest, originals = [], {}
    for area, action in CASES:
        directory = areas[area]
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / (action + ".canary")
        if action in ("read", "overwrite", "delete", "rename"):
            target.write_bytes(b"synthetic-original")
        name = area + ":" + action
        originals[name] = (target, target.read_bytes() if target.is_file() else None)
        manifest.append({"name": name, "action": action, "path": str(target.relative_to(root))})
    manifest.append({"name": "assigned-work:create", "action": "create",
                     "path": str((run_dir / "allowed.canary").relative_to(root))})
    (root / "probe-input.json").write_text(json.dumps(manifest), encoding="utf-8")

    native_popen = subprocess.Popen
    calls = []

    def compromised_worker(command, *args, **kwargs):
        assert command[2] == str(ROOT / "adapters/runner.py")
        assert command[3] == "verify"
        assert Path(kwargs["cwd"]) == run_dir
        calls.append({"cwd": str(kwargs["cwd"]), "env_keys": sorted(kwargs["env"])})
        substitute = [sys.executable, "-I", str(Path(__file__).with_name("confinement_probe.py")), str(root)]
        return native_popen(substitute, *args, **kwargs)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("nexus.host.subprocess.Popen", compromised_worker)
        host.busy.acquire()
        host._run(run_id)
    assert len(calls) == 1
    report = run_dir / "confinement-observations.json"
    assert report.is_file(), "Probe did not execute: confinement NOT PROVEN"
    values = json.loads(report.read_text(encoding="utf-8"))
    assert set(values) == {item["name"] for item in manifest}
    unchanged = {}
    for name, (target, original) in originals.items():
        unchanged[name] = (
            (target.is_file() and target.read_bytes() == original)
            if original is not None else not target.exists()
        ) and not target.with_name(target.name + ".moved").exists()
    result = {"scope": "actual Host launch, substituted hostile worker, synthetic targets only",
              "platform": sys.platform, "observations": values, "unchanged": unchanged,
              "host_status": host.store.state(run_id)["status"], "launch": calls[0]}
    evidence = os.environ.get("NEXUS_CONFINEMENT_EVIDENCE")
    if evidence:
        dest = Path(evidence)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def test_assigned_work_is_usable(observations):
    assert observations["observations"]["assigned-work:create"] == "ALLOWED"


def test_invalid_response_is_rejected(observations):
    assert observations["host_status"] == "BLOCKED"


@pytest.mark.parametrize("area,action", CASES)
def test_worker_cannot_cross_authority_boundary(observations, area, action):
    name = area + ":" + action
    assert observations["observations"][name] == "DENIED", (
        f"CONFINEMENT FAIL {name}: {observations['observations'][name]}; "
        "response validation is not OS isolation"
    )
    assert observations["unchanged"][name], f"Protected canary changed: {name}"
