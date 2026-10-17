import json
import subprocess
from types import SimpleNamespace

import pytest

from nexus.adapters.languagetool import normalize, run
from nexus.contracts import Blocked, validate


def response(matches=None):
    return {"software": {"name": "LanguageTool", "version": "test"},
            "warnings": {"incompleteResults": False},
            "language": {"code": "pt-PT"}, "matches": matches or []}


def test_suggestions_never_prove_correctness():
    result = normalize(json.dumps(response()))
    validate("result", result)
    assert result["status"] == "UNKNOWN"
    assert result["ai_calls"] == 0
    assert "não garante" in result["markdown"]


def test_suggestion_is_a_candidate():
    result = normalize(json.dumps(response([{"message": "Erro", "context": {"text": "ezemplo"},
                                             "replacements": [{"value": "exemplo"}]}])))
    validate("result", result)
    assert "exemplo" in result["markdown"]
    assert result["outcome"] == "candidate"


@pytest.mark.parametrize("raw", ["", "{}", "null", '{"matches":false}',
    json.dumps({**response(), "warnings": {"incompleteResults": True}}),
    json.dumps({**response(), "language": {"code": "en-US"}})])
def test_invalid_output_blocked(raw):
    with pytest.raises(Blocked):
        normalize(raw)


def setup(tmp_path):
    source = tmp_path / "input.bin"
    source.write_text("Um ezemplo.", encoding="utf-8")
    java, jar = tmp_path / "java.exe", tmp_path / "languagetool-commandline.jar"
    java.touch(); jar.touch()
    (tmp_path / "languagetool.json").write_text(json.dumps({"java": str(java), "jar": str(jar)}))
    return source


def test_missing_tool_blocked(tmp_path):
    source = setup(tmp_path)
    (tmp_path / "java.exe").unlink()
    with pytest.raises(Blocked):
        run(source)


def test_timeout_preserves_source(tmp_path, monkeypatch):
    # Adapter normalization/process unit double; separate native security gate.
    monkeypatch.setattr("nexus.adapters.languagetool.require_native_boundary", lambda: None)
    monkeypatch.setattr(subprocess, "CREATE_NO_WINDOW", getattr(subprocess, "CREATE_NO_WINDOW", 0), raising=False)
    source = setup(tmp_path)
    original = source.read_bytes()
    def timeout(*args, **kwargs):
        assert kwargs["input"] == b""
        raise subprocess.TimeoutExpired("java", 45)
    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(Blocked):
        run(source)
    assert source.read_bytes() == original


def test_tool_failure_rejected(tmp_path, monkeypatch):
    # Adapter normalization/process unit double; separate native security gate.
    monkeypatch.setattr("nexus.adapters.languagetool.require_native_boundary", lambda: None)
    monkeypatch.setattr(subprocess, "CREATE_NO_WINDOW", getattr(subprocess, "CREATE_NO_WINDOW", 0), raising=False)
    source = setup(tmp_path)
    def failed(*args, **kwargs):
        assert kwargs["input"] == b""
        return SimpleNamespace(returncode=1)
    monkeypatch.setattr(subprocess, "run", failed)
    with pytest.raises(Blocked):
        run(source)


def test_complete_diagnostic_retains_matches_beyond_display_limit():
    matches = [{"message": "Alerta " + str(index),
                "context": {"text": "trecho " + str(index)},
                "replacements": [{"value": "opção " + str(index)}],
                "offset": index, "length": 1,
                "rule": {"id": "RULE_" + str(index)}} for index in range(31)]
    original = response(matches)
    result = normalize(json.dumps(original))
    validate("result", result)
    stored = json.loads(result["evidence"][0]["value"])
    assert stored["version"] == "test"
    assert stored["matches"] == 31
    assert stored["diagnostic"] == original
    assert "- Alerta 30" not in result["markdown"]
    assert "diagnóstico completo foi conservado neste resultado" in result["markdown"]
    assert result["status"] == result["evidence"][0]["status"] == "UNKNOWN"
    assert result["outcome"] == "candidate" and result["ai_calls"] == 0


def test_complete_diagnostic_survives_result_json_round_trip():
    original = response([{"message": 'Aspas " e barra \\ — ação 😀',
                          "context": {"text": "linha 1\nlinha 2"},
                          "replacements": [{"value": "exemplo"}, {"value": "alternativa"}],
                          "offset": 0, "length": 2}])
    original["software"]["buildDate"] = "synthetic-build"
    original["language"]["detectedLanguage"] = {"code": "pt-PT", "confidence": 0.9}
    original["sentenceRanges"] = [[0, 12]]
    raw = json.dumps(original, ensure_ascii=False)
    result = normalize(raw)
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    restored = json.loads(encoded)
    assert json.loads(restored["evidence"][0]["value"])["diagnostic"] == original
    assert len(encoded) <= 1_000_000
    assert restored["evidence"][0]["capability"] == "languagetool.cli.pt-PT"


def test_complete_diagnostic_accepts_evidence_contract_boundary():
    original = response()
    original["extra"] = ""
    wrapper = {"version": "test", "matches": 0, "diagnostic": original}
    overhead = len(json.dumps(wrapper, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":"), allow_nan=False))
    original["extra"] = "x" * (100_000 - overhead)
    result = normalize(json.dumps(original))
    assert len(result["evidence"][0]["value"]) == 100_000
    assert json.loads(result["evidence"][0]["value"])["diagnostic"] == original
    validate("result", result)


def test_complete_diagnostic_rejects_excess_without_silent_truncation():
    original = response()
    original["extra"] = ""
    wrapper = {"version": "test", "matches": 0, "diagnostic": original}
    overhead = len(json.dumps(wrapper, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":"), allow_nan=False))
    original["extra"] = "x" * (100_001 - overhead)
    raw = json.dumps(original)
    with pytest.raises(Blocked, match="diagnóstico completo excede"):
        normalize(raw)
    assert json.loads(raw) == original

