"""Configure a pinned local Open Notebook through its public authenticated API.

Installation helper only. It never reads or writes Nexus Creative/Canonical.
Existing named configuration is preserved unless it exactly matches the Nexus
local contract; conflicts fail closed instead of being silently overwritten.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class SetupError(RuntimeError):
    pass


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key.strip()] = value
    return values


class API:
    def __init__(self, base: str, password: str):
        self.base = base.rstrip("/")
        self.password = password

    def call(self, method: str, path: str, payload=None):
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {"Authorization": "Bearer " + self.password, "Content-Type": "application/json"}
        request = Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=45) as response:
                raw = response.read()
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")[:2000]
            raise SetupError(f"Open Notebook API {method} {path} -> {error.code}: {body}") from error
        except URLError as error:
            raise SetupError(f"Open Notebook API unavailable: {error}") from error
        try:
            return json.loads(raw) if raw else None
        except json.JSONDecodeError as error:
            raise SetupError(f"Open Notebook returned invalid JSON for {path}") from error


def normalized_modalities(value) -> list[str]:
    return sorted(str(item) for item in (value or []))


def credential(api: API, provider: str, name: str, payload: dict):
    existing = api.call("GET", "/api/credentials/by-provider/" + quote(provider, safe=""))
    found = [item for item in existing if item.get("name") == name]
    if len(found) > 1:
        raise SetupError(f"Duplicate Open Notebook credential name: {name}")
    if found:
        item = found[0]
        if item.get("provider") != provider:
            raise SetupError(f"Credential provider mismatch: {name}")
        if normalized_modalities(item.get("modalities")) != normalized_modalities(payload.get("modalities")):
            raise SetupError(f"Credential modalities conflict: {name}")
        if (item.get("base_url") or None) != (payload.get("base_url") or None):
            raise SetupError(f"Credential base URL conflict: {name}")
        if bool(payload.get("api_key")) != bool(item.get("has_api_key")):
            raise SetupError(f"Credential key contract conflict: {name}")
        return item
    return api.call("POST", "/api/credentials", payload)


def model(api: API, *, name: str, provider: str, model_type: str, credential_id: str):
    items = api.call("GET", "/api/models")
    matches = [
        item for item in items
        if item.get("name") == name and item.get("provider") == provider and item.get("type") == model_type
    ]
    if len(matches) > 1:
        raise SetupError(f"Duplicate Open Notebook model: {provider}/{model_type}/{name}")
    if matches:
        item = matches[0]
        if item.get("credential") != credential_id:
            raise SetupError(f"Existing model is linked to another credential: {name}")
        return item
    return api.call("POST", "/api/models", {
        "name": name,
        "provider": provider,
        "type": model_type,
        "credential": credential_id,
    })


def speaker_profile(api: API, tts_id: str):
    name = "Nexus Local Test Speaker"
    path = "/api/speaker-profiles/" + quote(name, safe="")
    try:
        item = api.call("GET", path)
    except SetupError as error:
        if "-> 404:" not in str(error):
            raise
        item = None
    expected_speakers = [{
        "name": "Host",
        "voice_id": "af_heart",
        "backstory": "Local Nexus acceptance-test host.",
        "personality": "Clear, restrained and factual.",
    }]
    if item:
        if item.get("voice_model") != tts_id or item.get("speakers") != expected_speakers:
            raise SetupError("Existing Nexus speaker profile conflicts with the pinned local contract")
        return item
    return api.call("POST", "/api/speaker-profiles", {
        "name": name,
        "description": "Nexus local podcast acceptance profile.",
        "voice_model": tts_id,
        "speakers": expected_speakers,
    })


def episode_profile(api: API, language_id: str, speaker_id: str):
    name = "Nexus Local Test Episode"
    path = "/api/episode-profiles/" + quote(name, safe="")
    try:
        item = api.call("GET", path)
    except SetupError as error:
        if "-> 404:" not in str(error):
            raise
        item = None
    payload = {
        "name": name,
        "description": "Short fully local Nexus podcast acceptance profile.",
        "speaker_config": speaker_id,
        "outline_llm": language_id,
        "transcript_llm": language_id,
        "language": "en-US",
        "default_briefing": "Create a concise factual podcast from the selected material. Do not invent sources or claims.",
        "num_segments": 3,
        "max_tokens": 1200,
    }
    if item:
        checks = {
            "speaker_config": speaker_id,
            "outline_llm": language_id,
            "transcript_llm": language_id,
            "language": "en-US",
            "num_segments": 3,
            "max_tokens": 1200,
        }
        if any(item.get(key) != value for key, value in checks.items()):
            raise SetupError("Existing Nexus episode profile conflicts with the pinned local contract")
        return item
    return api.call("POST", "/api/episode-profiles", payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:5055")
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--authorize-install", action="store_true")
    args = parser.parse_args()
    if not args.authorize_install:
        raise SetupError("NEXUS_INSTALL_AUTHORIZATION_REQUIRED")
    values = read_env(args.env_file)
    password = values.get("OPEN_NOTEBOOK_PASSWORD", "")
    if not password:
        raise SetupError("OPEN_NOTEBOOK_PASSWORD is required for the local installation contract")
    api = API(args.api, password)

    ollama = credential(api, "ollama", "Nexus Local Ollama", {
        "name": "Nexus Local Ollama",
        "provider": "ollama",
        "modalities": ["language", "embedding"],
        "base_url": "http://127.0.0.1:11434",
        "num_ctx": 8192,
    })
    speech = credential(api, "openai_compatible", "Nexus Local Speech", {
        "name": "Nexus Local Speech",
        "provider": "openai_compatible",
        "modalities": ["text_to_speech"],
        "api_key": "nexus-local-not-a-secret",
        "base_url": "http://127.0.0.1:8969/v1",
    })

    for item in (ollama, speech):
        tested = api.call("POST", f"/api/credentials/{quote(item['id'], safe=':')}/test", {})
        if tested.get("success") is not True:
            raise SetupError(f"Provider test failed for {item['name']}: {tested.get('message')}")

    language = model(api, name="qwen3:4b", provider="ollama", model_type="language", credential_id=ollama["id"])
    embedding = model(api, name="nomic-embed-text", provider="ollama", model_type="embedding", credential_id=ollama["id"])
    tts = model(
        api,
        name="speaches-ai/Kokoro-82M-v1.0-ONNX",
        provider="openai_compatible",
        model_type="text_to_speech",
        credential_id=speech["id"],
    )

    defaults = api.call("PUT", "/api/models/defaults", {
        "default_chat_model": language["id"],
        "default_transformation_model": language["id"],
        "large_context_model": language["id"],
        "default_text_to_speech_model": tts["id"],
        "default_embedding_model": embedding["id"],
        "default_tools_model": language["id"],
    })
    expected_defaults = {
        "default_chat_model": language["id"],
        "default_transformation_model": language["id"],
        "large_context_model": language["id"],
        "default_text_to_speech_model": tts["id"],
        "default_embedding_model": embedding["id"],
        "default_tools_model": language["id"],
    }
    if any(defaults.get(key) != value for key, value in expected_defaults.items()):
        raise SetupError("Open Notebook default model assignment did not round-trip")

    settings = api.call("PUT", "/api/settings", {"auto_delete_files": "no"})
    if settings.get("auto_delete_files") != "no":
        raise SetupError("Open Notebook automatic file deletion could not be disabled")

    speaker = speaker_profile(api, tts["id"])
    episode = episode_profile(api, language["id"], speaker["id"])

    report = {
        "schema": "nexus.open-notebook-local-config.v1",
        "status": "PASS",
        "providers": {
            "ollama": {"credential_id": ollama["id"], "base_url": ollama.get("base_url")},
            "speech": {"credential_id": speech["id"], "base_url": speech.get("base_url")},
        },
        "models": {
            "language": {"id": language["id"], "name": language["name"]},
            "embedding": {"id": embedding["id"], "name": embedding["name"]},
            "tts": {"id": tts["id"], "name": tts["name"]},
        },
        "podcast_profiles": {
            "speaker": {"id": speaker["id"], "name": speaker["name"]},
            "episode": {"id": episode["id"], "name": episode["name"]},
        },
        "auto_delete_files": "no",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OPEN_NOTEBOOK_LOCAL_CONFIG=PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SetupError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
