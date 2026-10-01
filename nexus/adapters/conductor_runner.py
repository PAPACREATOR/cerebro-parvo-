"""Thin binding to Microsoft's engine. No Nexus workflow interpreter."""
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from nexus.contracts import Blocked, ROOT, strict_json
from conductor.config.loader import load_workflow
from conductor.engine.workflow import WorkflowEngine
from conductor.events import WorkflowEventEmitter


async def execute(workflow_path, inputs):
    config = load_workflow(workflow_path)
    if any(step.type not in ("script", "set") for step in config.agents):
        raise Blocked("Só são permitidos passos determinísticos neste adaptador.")
    events = []
    emitter = WorkflowEventEmitter()
    emitter.subscribe(lambda event: events.append(event.to_dict()))
    engine = WorkflowEngine(config, workflow_path=Path(workflow_path), event_emitter=emitter)
    # Intentionally no provider or registry. Cognition uses the explicit
    # Open Notebook HTTP capability, never Conductor's autonomous providers.
    result = await engine.run(inputs)
    return {"result": result["result"], "trace": {
        "engine": "microsoft/conductor", "version": "0.1.41",
        "summary": engine.get_execution_summary(), "events": events,
    }}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    process, input_path = sys.argv[1:3]
    if process not in ("verify", "interpret", "proofread"):
        raise SystemExit("Process unavailable")
    inputs = {
        "input_path": str(Path(input_path).resolve()),
        "python": sys.executable,
        "powershell": str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"),
    }
    response = asyncio.run(execute(ROOT / "processes" / (process + ".yaml"), inputs))
    print(json.dumps(response, ensure_ascii=False))
