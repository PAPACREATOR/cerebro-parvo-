"""External ACE-Step candidate contract; all provider calls are local fakes.

These are transport/format/recovery tests, NOT evidence that ACE-Step runs on
a physical PC or that a music result has entered sovereign Nexus Canonical.
"""
import hashlib
import io
import importlib.util
import json
from pathlib import Path
import wave

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "windows" / "ace_step_candidate.py"
spec = importlib.util.spec_from_file_location("nexus_ace_step_candidate_lab", SOURCE)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
ID = "550e8400-e29b-41d4-a716-446655440000"


def wav_bytes():
    stream = io.BytesIO()
    with wave.open(stream, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(16000)
        out.writeframes(b"\x00\x00" * 1600)
    return stream.getvalue()


def response(data):
    return json.dumps({"code": 200, "error": None, "data": data}).encode("utf-8")


def test_one_real_wav_candidate_contract_without_promoting(tmp_path, monkeypatch):
    audio = wav_bytes()
    called = []

    def fake(path, *, payload=None, secret="", **kwargs):
        called.append((path, payload, secret))
        if path == "/release_task":
            assert payload["audio_format"] == "wav"
            assert payload["model"] == "acestep-v15-turbo"
            assert payload["audio_duration"] == 10
            assert payload["prompt"] == "piano acústico"
            return response({"task_id": ID})
        if path == "/query_result":
            assert payload == {"task_id_list": [ID]}
            return response([{"task_id": ID, "status": 1, "result": json.dumps(
                [{"file": "/v1/audio?path=%2Ftmp%2Fmusic.wav"}])}])
        assert path == "/v1/audio?path=%2Ftmp%2Fmusic.wav"
        return audio

    monkeypatch.setattr(candidate, "request", fake)
    root = tmp_path / "candidate"
    result = candidate.produce("piano acústico", seconds=10, output=root, secret="test-secret")
    assert len(called) == 3
    assert all(item[2] == "test-secret" for item in called)
    assert result["status"] == "PASS_CANDIDATE"
    assert result["canonical_write"] is False
    assert result["authority"] == "NONE"
    assert result["wav"]["sha256"] == hashlib.sha256(audio).hexdigest()
    assert result["wav"]["sample_rate"] == 16000
    assert (root / "music-candidate.wav").read_bytes() == audio
    assert json.loads((root / "report.json").read_text()) == result
    assert not any(x.name in {"canonical", "creative", "store"} for x in root.parent.iterdir())


@pytest.mark.parametrize("path", [
    "http://127.0.0.1:8001.example.org/release_task",
    "http://127.0.0.1:8001/release_task",
    "//example.org/v1/audio?path=x",
    "/other/command", "/v1/audio?path=http%3A%2F%2Fexternal.org",
    "/v1/audio?path=%2Ftmp%2Fa.wav&other=x",
    "/v1/audio", "/query_result?foo=x",
])
def test_network_paths_are_strictly_fixed(path):
    with pytest.raises(candidate.CandidateError):
        candidate.request(path)


@pytest.mark.parametrize("raw", [
    b"", b"RIFF" + b"\x00" * 80,
    b"OggS" + b"\x00" * 100, b"RIFF\x00\x00\x00\x00WAVEnot-real",
])
def test_bogus_audio_does_not_claim_wav(raw):
    with pytest.raises(candidate.CandidateError):
        candidate.validate_wav(raw)


def test_malformed_foreign_task_is_never_downloaded(tmp_path, monkeypatch):
    calls = []

    def fake(path, *, payload=None, **_):
        calls.append(path)
        if path == "/release_task":
            return response({"task_id": ID})
        if path == "/query_result":
            return response([{"task_id": "other-task", "status": 1, "result": []}])
        pytest.fail("Downloaded unauthorized candidate")

    monkeypatch.setattr(candidate, "request", fake)
    with pytest.raises(candidate.CandidateError):
        candidate.produce("voz portuguesa", seconds=10, output=tmp_path / "candidate")
    assert calls == ["/release_task", "/query_result"]
    report = json.loads((tmp_path / "candidate" / "report.json").read_text())
    assert report["status"] == "RECOVERY_REQUIRED"
    assert report["task_id"] == ID
    assert not (tmp_path / "candidate" / "music-candidate.wav").exists()


def test_timeout_preserves_remote_id_and_never_resubmits(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(candidate.time, "monotonic", iter([0, 61]).__next__)
    monkeypatch.setattr(candidate, "request",
                        lambda path, **_: calls.append(path) or response({"task_id": ID}))
    with pytest.raises(candidate.CandidateError, match="do not auto-resubmit"):
        candidate.produce("folk", seconds=10, output=tmp_path / "candidate",
                          deadline_seconds=60)
    assert calls == ["/release_task"]
    state = json.loads((tmp_path / "candidate" / "report.json").read_text())
    assert state["status"] == "RECOVERY_REQUIRED"
    assert state["task_id"] == ID


def test_existing_output_never_overwritten_or_submitted(tmp_path, monkeypatch):
    out = tmp_path / "candidate"
    out.mkdir()
    (out / "original.txt").write_text("preserved")
    monkeypatch.setattr(candidate, "request", lambda *_a, **_kw: pytest.fail("Executed tool"))
    with pytest.raises(candidate.CandidateError, match="already exist"):
        candidate.produce("folk", seconds=10, output=out)
    assert (out / "original.txt").read_text() == "preserved"


def test_authorization_flag_required_before_remote_production(monkeypatch):
    monkeypatch.setattr(candidate.sys, "argv",
                        ["ace_step_candidate.py", "--prompt", "folk", "--output", "unused"])
    monkeypatch.setattr(candidate, "produce", lambda *_a, **_kw: pytest.fail("Executed tool"))
    with pytest.raises(candidate.CandidateError, match="Explicit human"):
        candidate.main()
