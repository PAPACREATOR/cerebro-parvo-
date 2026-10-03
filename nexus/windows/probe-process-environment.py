"""Synthetic CI probe: compare PowerShell stdin/environment without user data."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nexus.host import process_environment
from nexus.contracts import ROOT
from ruamel.yaml import YAML


with tempfile.TemporaryDirectory(prefix="nexus-process-probe-") as directory:
    work = Path(directory)
    source = work / "synthetic.txt"
    source.write_bytes(b"Nexus synthetic environment probe\n")
    workflow = YAML(typ="safe").load((ROOT / "processes/verify.yaml").read_text("utf-8"))
    step = next(s for s in workflow["agents"] if s["name"] == "hash_windows")
    args = list(step["args"])
    args[-1] = args[-1].replace(
        "$p = [Console]::In.ReadToEnd().TrimEnd([char]10, [char]13)",
        "[Console]::Error.WriteLine('BEFORE_STDIN')\n"
        "$p = [Console]::In.ReadToEnd().TrimEnd([char]10, [char]13)\n"
        "[Console]::Error.WriteLine('AFTER_STDIN')",
    )
    executable = str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe")
    minimal = process_environment(work)
    system_modules = str(Path(executable).parent / "Modules")
    without_cache_override = {key: value for key, value in minimal.items() if key != "PSModuleAnalysisCachePath"}
    cases = [
        ("minimal_private_cache", minimal, subprocess.CREATE_NO_WINDOW),
        ("minimal_private_cache_system_modules", {**minimal, "PSModulePath": system_modules}, subprocess.CREATE_NO_WINDOW),
        ("minimal_without_cache_override", without_cache_override, subprocess.CREATE_NO_WINDOW),
    ]
    for label, environment, flags in cases:
        try:
            result = subprocess.run(
                [executable, *args], input=str(source).encode("utf-8"),
                capture_output=True, timeout=8, env=environment, cwd=work,
                creationflags=flags,
            )
            record = dict(case=label, returncode=result.returncode,
                          stdout=result.stdout.decode("utf-8", errors="replace"),
                          stderr=result.stderr.decode("utf-8", errors="replace"))
        except subprocess.TimeoutExpired as error:
            record = dict(case=label, timeout=True,
                          stdout=(error.stdout or b"").decode("utf-8", errors="replace"),
                          stderr=(error.stderr or b"").decode("utf-8", errors="replace"))
        print(json.dumps(record, ensure_ascii=False), flush=True)
