"""ACE-Step 1.5 local WAV candidate bridge; NOT a Nexus execution authority.

Explicitly operator-started acceptance/lab entrypoint. Host/Store/Canonical are
never imported. A valid WAV plus a SHA-256 receipt proves an external tool
returned bytes; a successful /health probe alone does not. Never auto-retry a
submitted external task after an uncertain timeout.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import wave

BASE = "http://127.0.0.1:8001"
MAX_HTTP_JSON = 500_000
MAX_WAV_BYTES = 100_000_000


class CandidateError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        raise CandidateError("External tool redirect is forbidden")


def request(path: str, *, payload: dict | None = None, secret: str = "",
            max_bytes: int = MAX_HTTP_JSON, timeout: int = 20) -> bytes:
    parsed = urllib.parse.urlsplit(path)
    if (parsed.scheme or parsed.netloc or parsed.fragment
            or not parsed.path.startswith("/") or parsed.path.startswith("//")
            or parsed.path not in {"/release_task", "/query_result", "/v1/audio"}
            or (parsed.query and parsed.path != "/v1/audio")):
        raise CandidateError("Unexpected ACE-Step API path")
    if parsed.path == "/v1/audio":
        values = urllib.parse.parse_qs(parsed.query, strict_parsing=True)
        if set(values) != {"path"} or len(values["path"]) != 1:
            raise CandidateError("Invalid ACE-Step audio reference")
        file_ref = values["path"][0]
        if (not file_ref.startswith("/") or "\x00" in file_ref
                or len(file_ref) > 2048 or "\\" in file_ref):
            raise CandidateError("ACE-Step audio reference is invalid")
    raw = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "audio/wav" if parsed.path == "/v1/audio" else "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if secret:
        headers["Authorization"] = "Bearer " + secret
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(urllib.request.Request(BASE + path, data=raw, headers=headers,
                            method="POST" if raw is not None else "GET"), timeout=timeout) as response:
            if response.status != 200:
                raise CandidateError("ACE-Step returned a non-success status")
            result = response.read(max_bytes + 1)
    except CandidateError:
        raise
    except (OSError, urllib.error.URLError, ValueError) as error:
        raise CandidateError("ACE-Step local API unavailable or malformed") from error
    if len(result) > max_bytes:
        raise CandidateError("ACE-Step output exceeds bounded size")
    return result


def wrapped(data: bytes):
    try:
        value = json.loads(data)
    except (UnicodeError, ValueError) as error:
        raise CandidateError("ACE-Step returned invalid JSON") from error
    if not isinstance(value, dict) or value.get("code") != 200 or value.get("error") is not None:
        raise CandidateError("ACE-Step rejected the task")
    return value.get("data")


def validate_wav(raw: bytes) -> dict:
    if (len(raw) < 44 or len(raw) > MAX_WAV_BYTES or raw[:4] != b"RIFF"
            or raw[8:12] != b"WAVE"):
        raise CandidateError("ACE-Step returned no bounded RIFF/WAVE")
    try:
        with wave.open(io.BytesIO(raw), "rb") as stream:
            channels = stream.getnchannels()
            rate = stream.getframerate()
            frames = stream.getnframes()
            duration = frames / rate if rate else 0
            if (not 1 <= channels <= 2 or not 8000 <= rate <= 192000
                    or not 1 <= frames or not 0 < duration <= 600):
                raise CandidateError("ACE-Step WAV parameters invalid")
            return {"channels": channels, "sample_rate": rate,
                    "frames": frames, "duration_seconds": round(duration, 3)}
    except (wave.Error, EOFError, OSError) as error:
        raise CandidateError("ACE-Step WAV payload invalid") from error


def produce(prompt: str, *, seconds: int, output: Path, lyrics: str = "",
            secret: str = "", deadline_seconds: int = 1800, poll_seconds: int = 4) -> dict:
    if (not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 1500
            or "\x00" in prompt or not isinstance(lyrics, str)
            or len(lyrics) > 5000 or "\x00" in lyrics or type(seconds) is not int
            or not 10 <= seconds <= 180 or not 60 <= deadline_seconds <= 3600
            or not 1 <= poll_seconds <= 30):
        raise CandidateError("Invalid bounded music request")
    output = Path(output).resolve()
    if output.exists():
        raise CandidateError("Output directory must not already exist")
    output.mkdir(parents=True)
    receipt = {"schema": "nexus.ace-step-candidate.v1", "status": "PREPARED",
               "authority": "NONE", "canonical_write": False,
               "provider": "ace-step-1.5", "endpoint": BASE, "source_sha256":
               hashlib.sha256((prompt + "\n" + lyrics).encode("utf-8")).hexdigest()}
    report = output / "report.json"

    def save():
        report.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")

    save()
    try:
        payload = {"prompt": prompt.strip(), "lyrics": lyrics, "audio_duration": seconds,
                   "audio_format": "wav", "model": "acestep-v15-turbo", "thinking": False}
        response = wrapped(request("/release_task", payload=payload, secret=secret))
        task_id = response.get("task_id") if isinstance(response, dict) else None
        if not isinstance(task_id, str) or not re.fullmatch(r"[0-9a-fA-F-]{16,64}", task_id):
            raise CandidateError("ACE-Step did not return a bounded task ID")
        receipt.update(status="EXTERNAL_TASK_SUBMITTED", task_id=task_id)
        save()
        until = time.monotonic() + deadline_seconds
        while time.monotonic() < until:
            batch = wrapped(request("/query_result",
                                    payload={"task_id_list": [task_id]}, secret=secret))
            if not isinstance(batch, list) or len(batch) > 1:
                raise CandidateError("ACE-Step task status shape invalid")
            if not batch:
                time.sleep(poll_seconds)
                continue
            item = batch[0]
            if not isinstance(item, dict) or item.get("task_id") != task_id:
                raise CandidateError("ACE-Step returned a different task ID")
            status = item.get("status")
            if status == 2:
                raise CandidateError("ACE-Step explicitly failed generation")
            if status == 0:
                time.sleep(poll_seconds)
                continue
            if status != 1:
                raise CandidateError("ACE-Step task status unknown")
            value = item.get("result")
            try:
                files = json.loads(value) if isinstance(value, str) else value
            except ValueError as error:
                raise CandidateError("ACE-Step result JSON invalid") from error
            if not isinstance(files, list) or len(files) != 1 or not isinstance(files[0], dict):
                raise CandidateError("ACE-Step did not produce exactly one file")
            audio_url = files[0].get("file")
            if not isinstance(audio_url, str) or not audio_url.startswith("/v1/audio?path="):
                raise CandidateError("ACE-Step audio URL not locally bounded")
            raw = request(audio_url, secret=secret, max_bytes=MAX_WAV_BYTES, timeout=180)
            meta = validate_wav(raw)
            candidate = output / "music-candidate.wav"
            candidate.write_bytes(raw)
            receipt.update(status="PASS_CANDIDATE", wav={
                "name": candidate.name, "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(), **meta})
            save()
            return receipt
        raise CandidateError("ACE-Step task still unresolved; inspect task ID, do not auto-resubmit")
    except Exception:
        if receipt["status"] != "PREPARED":
            receipt["status"] = "RECOVERY_REQUIRED"
        else:
            receipt["status"] = "FAIL"
        save()
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--lyrics", default="")
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--authorize-production", action="store_true")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()
    if not args.authorize_production:
        raise CandidateError("Explicit human production command required")
    produce(args.prompt, seconds=args.seconds, lyrics=args.lyrics,
            output=args.output, secret=os.environ.get("ACESTEP_API_KEY", ""),
            deadline_seconds=args.timeout)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CandidateError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
