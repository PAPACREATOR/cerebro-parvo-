"""Opt-in real Windows verify + LanguageTool through Host, with no replay.

H1 confirmations below are programmatic fixtures. H2 is NOT RUN, and no
Canonical promotion or physical human acceptance is claimed by this test.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError

import pytest

from nexus.contracts import strict_json, validate
from nexus.host import Host
from nexus.tests.test_reverse_flow import http


pytestmark = pytest.mark.skipif(
    os.environ.get("NEXUS_REAL_VERIFY_PROOFREAD") != "1",
    reason="Explicit real verify/LanguageTool Windows gate NOT RUN here",
)


def test_real_verify_then_languagetool_retains_diagnostic_and_recovers_without_replay(tmp_path, monkeypatch):
    # With the explicit opt-in flag, missing prerequisites are FAIL, not SKIP.
    assert os.name == "nt", "This native integration gate requires Windows"
    paths = {}
    for variable, expected in (("NEXUS_LANGUAGETOOL_JAVA", "java.exe"),
                               ("NEXUS_LANGUAGETOOL_JAR", "languagetool-commandline.jar")):
        value = os.environ.get(variable)
        assert value, "Missing native gate prerequisite: " + variable
        path = Path(value)
        assert path.is_absolute() and path.is_file(), variable
        assert path.name.lower() == expected, variable
        paths[variable] = path

    from nexus import host as host_module
    real_launch = host_module.launch_confined
    java_diagnostics = []
    launches = []

    def observed_launch(command, **options):
        # Observe the SAME real confined process; never replace its output.
        worker = real_launch(command, **options)
        launches.append(tuple(command))
        communicate = worker.communicate

        def observed_communication(*args, **kwargs):
            try:
                return communicate(*args, **kwargs)
            finally:
                diagnostic = Path(options["cwd"]) / "languagetool-output.json"
                if diagnostic.is_file():
                    java_diagnostics.append(diagnostic.read_bytes())

        worker.communicate = observed_communication
        return worker

    monkeypatch.setattr(host_module, "launch_confined", observed_launch)
    folder = tmp_path / "real-verify-proofread"
    folder.mkdir()
    (folder / "languagetool.json").write_text(json.dumps({
        "java": str(paths["NEXUS_LANGUAGETOOL_JAVA"]),
        "jar": str(paths["NEXUS_LANGUAGETOOL_JAR"]),
    }), encoding="utf-8")
    source_text = "Isto é um ezemplo de texto em português.\nA fonte é sintética e deve ficar intacta.\n"
    assert len(source_text) <= 6000
    raw = source_text.encode("utf-8")
    source_hash = hashlib.sha256(raw).hexdigest()
    original = {"filename": "texto-ação.txt", "attachment": base64.b64encode(raw).decode("ascii")}
    original_intent = "Verifica este texto e revê o português"
    host = Host(folder)
    runs = []
    used_tickets = []

    def wait_for_candidate(call, run_id):
        # New test observation budget only. Host Shell/worker and Java budgets
        # stay unchanged (12/75/45 s); this does not retry or extend a tool.
        deadline = time.monotonic() + 120
        state = call("/api/runs/" + run_id)
        while state["status"] == "RUNNING" and time.monotonic() < deadline:
            time.sleep(0.1)
            state = call("/api/runs/" + run_id)
        assert state["status"] == "HUMAN_REQUIRED", state
        # Store.accept presents the candidate before _run's finally releases
        # busy. Observe that same worker finishing before starting step two.
        assert host.busy.acquire(timeout=max(0, deadline - time.monotonic())), "Host cleanup did not finish"
        host.busy.release()
        return state

    def execute_step(call, step):
        proposal = {"text": "& " + step["command"], **original}
        prepared = call("/api/prepare-run", proposal)
        assert prepared["process"] == step["process"]
        assert prepared["attachment_sha256"] == source_hash
        ticket = prepared["ticket"]
        used_tickets.append((ticket, proposal))
        run_id = call("/api/confirm-run", {
            "ticket": ticket, "confirmed": True, **proposal,
        })["run_id"]
        runs.append(run_id)
        state = wait_for_candidate(call, run_id)
        with pytest.raises(HTTPError) as replay:
            call("/api/confirm-run", {"ticket": ticket, "confirmed": True, **proposal})
        assert replay.value.code == 403
        assert state["process_id"] == step["process"]
        assert state["input_sha256"] == source_hash
        assert (folder / "runs" / run_id / "input.bin").read_bytes() == raw
        assert not (folder / "canonical" / run_id).exists()
        host.store.check_candidate(host.store.state(run_id))
        return run_id, state

    try:
        with http(host) as call:
            preview = call("/api/interpret", {"text": original_intent})
            plan = preview["composite"]
            assert plan["authority"] == "NONE" and plan["execution"] == "NOT_AUTHORIZED"
            assert plan["requires_human_confirmation"] is True
            assert [step["process"] for step in plan["steps"]] == ["verify", "proofread"]
            assert call("/api/runs") == []
            with pytest.raises(HTTPError) as direct:
                call("/api/run", {"process": "verify", "text": "& verificar integridade de ficheiro", **original})
            assert direct.value.code == 403

            verify_run, verified = execute_step(call, plan["steps"][0])
            assert verified["result"]["status"] == "PASS"
            assert verified["result"]["outcome"] == "agreement"
            evidence = verified["result"]["evidence"]
            assert {item["capability"] for item in evidence} == {"windows.cng-sha256", "python.hashlib"}
            assert all(item["status"] == "PASS" and item["value"] == source_hash for item in evidence)

            # A rejected/changed second H1 must never call LanguageTool.
            second = {"text": "& " + plan["steps"][1]["command"], **original}
            pending = call("/api/prepare-run", second)
            assert call("/api/confirm-run", {
                "ticket": pending["ticket"], "confirmed": False, **second,
            }) == {"status": "CANCELLED"}
            with pytest.raises(HTTPError) as cancelled_replay:
                call("/api/confirm-run", {"ticket": pending["ticket"], "confirmed": True, **second})
            assert cancelled_replay.value.code == 403
            pending = call("/api/prepare-run", second)
            changed = {**second, "attachment": base64.b64encode(raw + b"changed").decode("ascii")}
            with pytest.raises(HTTPError) as changed_source:
                call("/api/confirm-run", {"ticket": pending["ticket"], "confirmed": True, **changed})
            assert changed_source.value.code == 403
            assert len(call("/api/runs")) == 1
            assert java_diagnostics == []

            proofread_run, reviewed = execute_step(call, plan["steps"][1])
            assert proofread_run != verify_run
            result = reviewed["result"]
            assert result["status"] == "UNKNOWN" and result["outcome"] == "candidate"
            assert result["ai_calls"] == 0 and "artifact" not in result
            assert len(result["evidence"]) == 1
            language_evidence = result["evidence"][0]
            assert language_evidence["capability"] == "languagetool.cli.pt-PT"
            assert language_evidence["status"] == "UNKNOWN"
            metadata = strict_json(language_evidence["value"])
            diagnostic = validate("languagetool", metadata["diagnostic"])
            assert metadata["version"] == diagnostic["software"]["version"] == "6.6"
            assert diagnostic["warnings"]["incompleteResults"] is False
            assert diagnostic["language"]["code"] == "pt-PT"
            assert metadata["matches"] == len(diagnostic["matches"]) >= 1
            assert len(java_diagnostics) == 1
            assert strict_json(java_diagnostics[0]) == diagnostic
            execution = strict_json((folder / "runs" / proofread_run / "execution.stdout.json").read_bytes())
            assert execution["result"] == result
            assert len(call("/api/runs")) == 2 and len(launches) == 2
            assert not list((folder / "canonical").iterdir())

            receipt_request = {"text": original_intent, "filename": original["filename"],
                               "input_sha256": source_hash, "verify_run_id": verify_run,
                               "proofread_run_id": proofread_run}
            receipt = call("/api/flow-receipt", receipt_request)
            assert receipt["authority"] == "NONE" and receipt["execution"] == "NOT_AUTHORIZED"
            assert receipt["human_approval_required"] is True
            assert "product" not in receipt
            assert [step["run_id"] for step in receipt["steps"]] == runs
            assert receipt["comparison"] == {
                "input_sha256": source_hash, "original_preserved": True,
                "integrity": "PASS", "proofreading": "UNKNOWN",
                "alerts": len(diagnostic["matches"]), "text_correctness": "NOT_ESTABLISHED",
            }
    finally:
        # On a failure observe completion of the SAME worker, never rerun or
        # remove busy/alter the native boundary to make this test pass.
        assert host.busy.acquire(timeout=120), "The existing Host worker did not finish cleanup"
        host.busy.release()

    package = {str(path.relative_to(folder)): path.read_bytes()
               for area in ("runs", "creative", "canonical")
               for path in (folder / area).rglob("*") if path.is_file()}

    def no_replay(*_args, **_kwargs):
        pytest.fail("Recovery or receipt replayed an execution/tool/subprocess")

    monkeypatch.setattr(Host, "start", no_replay)
    monkeypatch.setattr(host_module, "launch_confined", no_replay)
    monkeypatch.setattr("nexus.adapters.runner.prepare_task", no_replay)
    monkeypatch.setattr("nexus.adapters.languagetool.run", no_replay)
    monkeypatch.setattr(subprocess, "run", no_replay)
    monkeypatch.setattr(subprocess, "Popen", no_replay)
    restored = Host(folder)
    for run_id in runs:
        restored.store.check_candidate(restored.store.state(run_id))
        assert restored.store.state(run_id)["status"] == "HUMAN_REQUIRED"
    with http(restored) as call:
        recovered = call("/api/flow-receipt", receipt_request)
        assert recovered == receipt
        for ticket, proposal in used_tickets:
            with pytest.raises(HTTPError) as stale:
                call("/api/confirm-run", {"ticket": ticket, "confirmed": True, **proposal})
            assert stale.value.code == 403
        assert len(call("/api/runs")) == 2
        assert call("/api/runs/" + proofread_run)["result"] == result
    assert {str(path.relative_to(folder)): path.read_bytes()
            for area in ("runs", "creative", "canonical")
            for path in (folder / area).rglob("*") if path.is_file()} == package
    assert not list((folder / "canonical").iterdir())
    print(json.dumps({"route": "real Windows verify -> real LanguageTool",
                      "source_sha256": source_hash, "run_ids": runs,
                      "languagetool_version": metadata["version"], "matches": metadata["matches"],
                      "diagnostic_equal_to_real_java_output": True,
                      "receipt_sha256": receipt["receipt_sha256"],
                      "h1": "PROGRAMMATIC_FIXTURE_PER_STEP", "h2": "NOT_RUN",
                      "canonical_promotion": False, "recovery": "NO_REPLAY"}, ensure_ascii=False))
