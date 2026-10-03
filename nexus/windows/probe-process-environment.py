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
    args[-1] = args[-1].replace(
        "$algorithm = [System.Security.Cryptography.SHA256]::Create()",
        "[Console]::Error.WriteLine('BEFORE_CREATE')\n"
        "$algorithm = [System.Security.Cryptography.SHA256]::Create()\n"
        "[Console]::Error.WriteLine('AFTER_CREATE')",
    ).replace(
        "@{status='PASS'; sha256=$hash; capability='windows.dotnet-sha256'} | ConvertTo-Json -Compress",
        "[Console]::Error.WriteLine('BEFORE_JSON')\n"
        "@{status='PASS'; sha256=$hash; capability='windows.dotnet-sha256'} | ConvertTo-Json -Compress\n"
        "[Console]::Error.WriteLine('AFTER_JSON')",
    )
    executable = str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe")
    minimal = process_environment(work)
    system_modules = str(Path(executable).parent / "Modules")
    without_cache_override = {key: value for key, value in minimal.items() if key != "PSModuleAnalysisCachePath"}
    raw_json_args = list(args)
    raw_json_args[-1] = raw_json_args[-1].replace(
        "@{status='PASS'; sha256=$hash; capability='windows.dotnet-sha256'} | ConvertTo-Json -Compress",
        "[Console]::Out.WriteLine('{\"status\":\"PASS\",\"sha256\":\"' + $hash + '\",\"capability\":\"windows.dotnet-sha256\"}')",
    )
    cases = [
        ("minimal_progress", minimal, args),
        ("minimal_direct_json", minimal, raw_json_args),
    ]
    for label, environment, command_args in cases:
        try:
            result = subprocess.run(
                [executable, *command_args], input=str(source).encode("utf-8"),
                capture_output=True, timeout=8, env=environment, cwd=work,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            record = dict(case=label, returncode=result.returncode,
                          stdout=result.stdout.decode("utf-8", errors="replace"),
                          stderr=result.stderr.decode("utf-8", errors="replace"))
        except subprocess.TimeoutExpired as error:
            record = dict(case=label, timeout=True,
                          stdout=(error.stdout or b"").decode("utf-8", errors="replace"),
                          stderr=(error.stderr or b"").decode("utf-8", errors="replace"))
        print(json.dumps(record, ensure_ascii=False), flush=True)
