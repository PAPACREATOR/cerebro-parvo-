"""Opt-in physical Windows acceptance probes for external Nexus capabilities.

This module is deliberately outside the authoritative Host process catalogue.
It exercises real local services and writes only to an operator-selected report
folder. A PASS here is evidence for the physical tool; it does not promote
anything to Canonical or claim Host integration where that integration does not
yet exist.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAX_JSON = 4_000_000
MAX_MEDIA = 200_000_000


class NotConfigured(RuntimeError):
    pass


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def request_bytes(url: str, *, method: str = "GET", payload=None, headers=None,
                  timeout: float = 20, max_bytes: int = MAX_JSON) -> tuple[bytes, dict]:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    merged = {"User-Agent": "Nexus-Local-Acceptance/1.0"}
    if payload is not None:
        merged["Content-Type"] = "application/json"
    if headers:
        merged.update(headers)
    req = urllib.request.Request(url, data=data, headers=merged, method=method)
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=timeout) as response:
            raw = response.read(max_bytes + 1)
            meta = {k.lower(): v for k, v in response.headers.items()}
            meta["status"] = response.status
            meta["url"] = response.geturl()
    except urllib.error.HTTPError as error:
        body = error.read(200_000).decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {body[:2000]}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise NotConfigured(str(error)) from None
    if len(raw) > max_bytes:
        raise RuntimeError("response too large")
    return raw, meta


def request_json(url: str, **kwargs):
    raw, meta = request_bytes(url, **kwargs)
    try:
        return json.loads(raw), meta
    except (ValueError, UnicodeError):
        raise RuntimeError("invalid JSON response") from None


def local_config() -> dict:
    path = ROOT / "nexus" / "runtime" / "open-notebook.json"
    if not path.is_file():
        raise NotConfigured("nexus/runtime/open-notebook.json missing")
    value = json.loads(path.read_text(encoding="utf-8"))
    base = value.get("base_url")
    password = value.get("password")
    if base != "http://127.0.0.1:5055" or not isinstance(password, str) or not password:
        raise NotConfigured("OpenNotebook local configuration incomplete")
    return {"base_url": base, "password": password}


def on_headers(config: dict) -> dict:
    return {"Authorization": "Bearer " + config["password"], "Accept": "application/json"}


def _names(value) -> list[str]:
    if isinstance(value, dict):
        for key in ("items", "data", "profiles", "results"):
            if isinstance(value.get(key), list):
                value = value[key]
                break
    if not isinstance(value, list):
        return []
    return [item.get("name") for item in value if isinstance(item, dict)
            and isinstance(item.get("name"), str) and item.get("name").strip()]


def _profile_endpoint(openapi: dict, fragment: str) -> str | None:
    candidates = []
    for path, operations in openapi.get("paths", {}).items():
        normalized = path.lower().replace("_", "-")
        if fragment in normalized and isinstance(operations, dict) and "get" in operations:
            candidates.append(path)
    exact = [p for p in candidates if "{" not in p]
    return sorted(exact, key=len)[0] if exact else None


def zotero(query: str, out: Path) -> dict:
    base = "http://127.0.0.1:23119/api/"
    try:
        _, root_meta = request_bytes(base, headers={"Zotero-API-Version": "3"}, timeout=5)
    except NotConfigured:
        raise
    params = urllib.parse.urlencode({
        "format": "json", "limit": "10", "q": query, "qmode": "everything"
    })
    value, meta = request_json(
        base + "users/0/items?" + params,
        headers={"Zotero-API-Version": "3"}, timeout=15,
    )
    if not isinstance(value, list):
        raise RuntimeError("Zotero items response is not a list")
    compact = []
    for item in value[:10]:
        data = item.get("data", item) if isinstance(item, dict) else {}
        if not isinstance(data, dict):
            continue
        compact.append({
            "key": data.get("key") or (item.get("key") if isinstance(item, dict) else None),
            "itemType": data.get("itemType"),
            "title": data.get("title", ""),
            "date": data.get("date", ""),
        })
    result = {
        "status": "PASS",
        "capability": "zotero.local-read-search",
        "authority": "NONE",
        "query": query,
        "matches": len(compact),
        "items": compact,
        "server_id": meta.get("zotero-server-id") or root_meta.get("zotero-server-id"),
        "note": "Read-only local API search. No Zotero write was attempted.",
    }
    write_json(out / "zotero-search.json", result)
    return result


def internet_research(query: str, out: Path) -> dict:
    params = urllib.parse.urlencode({
        "action": "query", "list": "search", "srsearch": query,
        "srlimit": "5", "format": "json", "utf8": "1",
    })
    value, _ = request_json(
        "https://pt.wikipedia.org/w/api.php?" + params,
        timeout=20,
    )
    rows = value.get("query", {}).get("search", []) if isinstance(value, dict) else []
    if not isinstance(rows, list):
        raise RuntimeError("internet search response invalid")
    results = []
    for row in rows[:5]:
        if not isinstance(row, dict) or not isinstance(row.get("title"), str):
            continue
        title = row["title"]
        results.append({
            "title": title,
            "pageid": row.get("pageid"),
            "url": "https://pt.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
        })
    result = {
        "status": "PASS",
        "capability": "internet.research-smoke.wikipedia",
        "authority": "NONE",
        "query": query,
        "results": results,
        "note": "Physical outbound research smoke only; this is not yet an authorized Host @web process.",
    }
    write_json(out / "internet-search.json", result)
    return result


def ace_music(out: Path) -> dict:
    base = "http://127.0.0.1:8001"
    headers = {"Accept": "application/json"}
    token = os.environ.get("ACESTEP_API_KEY", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    health, _ = request_json(base + "/health", headers=headers, timeout=8)
    data = health.get("data") if isinstance(health, dict) else None
    if not isinstance(data, dict) or data.get("status") != "ok":
        raise NotConfigured("ACE-Step health endpoint is not ready")
    if data.get("models_initialized") is False:
        raise NotConfigured("ACE-Step models are not initialized")

    payload = {
        "prompt": "instrumental minimalista, piano quente e textura eletrónica discreta, sem imitar artista específico",
        "lyrics": "",
        "thinking": False,
        "audio_duration": 15,
        "inference_steps": 8,
        "audio_format": "mp3",
        "vocal_language": "pt",
    }
    submitted, _ = request_json(base + "/release_task", method="POST", payload=payload,
                                headers=headers, timeout=30)
    if not isinstance(submitted, dict) or submitted.get("code") != 200:
        raise RuntimeError("ACE-Step task submission failed")
    task_id = (submitted.get("data") or {}).get("task_id")
    if not isinstance(task_id, str) or not task_id:
        raise RuntimeError("ACE-Step did not return a task id")

    deadline = time.monotonic() + 900
    item = None
    while time.monotonic() < deadline:
        state, _ = request_json(
            base + "/query_result", method="POST",
            payload={"task_id_list": [task_id]}, headers=headers, timeout=30,
        )
        rows = state.get("data") if isinstance(state, dict) else None
        if isinstance(rows, list) and rows:
            item = rows[0]
            status = item.get("status")
            if status == 1:
                break
            if status == 2:
                raise RuntimeError("ACE-Step generation reported failure")
        time.sleep(2)
    else:
        raise RuntimeError("ACE-Step generation timeout")

    try:
        generated = json.loads(item["result"])
        audio_ref = generated[0]["file"]
    except (KeyError, IndexError, TypeError, ValueError):
        raise RuntimeError("ACE-Step result envelope invalid") from None
    if not isinstance(audio_ref, str) or not audio_ref.startswith("/v1/audio?"):
        raise RuntimeError("ACE-Step returned an unexpected audio reference")

    raw, _ = request_bytes(base + audio_ref, headers=headers, timeout=120, max_bytes=MAX_MEDIA)
    if len(raw) < 1000:
        raise RuntimeError("ACE-Step audio is unexpectedly small")
    audio = out / "musica-teste.mp3"
    audio.write_bytes(raw)
    result = {
        "status": "PASS", "capability": "ace-step.real-generation",
        "authority": "UNTRUSTED", "outcome": "candidate",
        "task_id": task_id, "file": audio.name, "bytes": len(raw), "sha256": sha256(raw),
        "note": "Physical generation only. It is not promoted to Nexus Canonical.",
    }
    write_json(out / "ace-step-music.json", result)
    return result


def podcast(out: Path) -> dict:
    config = local_config()
    base, headers = config["base_url"], on_headers(config)
    try:
        openapi, _ = request_json(base + "/openapi.json", timeout=10)
    except RuntimeError:
        openapi, _ = request_json(base + "/openapi.json", headers=headers, timeout=10)

    ep_path = _profile_endpoint(openapi, "episode-profile")
    sp_path = _profile_endpoint(openapi, "speaker-profile")
    if not ep_path or not sp_path:
        raise NotConfigured("OpenNotebook profile endpoints not found")
    episodes, _ = request_json(base + ep_path, headers=headers, timeout=20)
    speakers, _ = request_json(base + sp_path, headers=headers, timeout=20)
    ep_names, sp_names = _names(episodes), _names(speakers)
    if not ep_names or not sp_names:
        raise NotConfigured("OpenNotebook podcast profiles are not configured")

    episode_name = "Nexus teste físico " + time.strftime("%Y%m%d-%H%M%S")
    content = (
        "O Nexus é um sistema local-first em protótipo. "
        "Este ensaio deve explicar em português, de forma factual, a diferença entre "
        "Creative, aprovação humana e Canonical. Não inventar capacidades."
    )
    payload = {
        "episode_profile": ep_names[0],
        "speaker_profile": sp_names[0],
        "episode_name": episode_name,
        "notebook_id": None,
        "content": content,
        "briefing_suffix": "Teste curto de aceitação. Manter linguagem simples e factual.",
    }
    submitted, _ = request_json(base + "/api/podcasts/generate", method="POST",
                                payload=payload, headers=headers, timeout=30)
    job_id = submitted.get("job_id") if isinstance(submitted, dict) else None
    if not isinstance(job_id, str) or not job_id:
        raise RuntimeError("OpenNotebook podcast did not return a job id")

    deadline = time.monotonic() + 900
    last = None
    while time.monotonic() < deadline:
        last, _ = request_json(base + "/api/podcasts/jobs/" + urllib.parse.quote(job_id, safe=""),
                               headers=headers, timeout=30)
        status = str(last.get("status", "")).lower() if isinstance(last, dict) else ""
        if status in {"completed", "complete", "success", "succeeded", "done"}:
            break
        if status in {"failed", "error", "cancelled", "canceled"}:
            raise RuntimeError("OpenNotebook podcast job failed: " + json.dumps(last, ensure_ascii=False)[:1500])
        time.sleep(3)
    else:
        raise RuntimeError("OpenNotebook podcast generation timeout")

    items, _ = request_json(base + "/api/podcasts/episodes", headers=headers, timeout=30)
    episode = next((x for x in items if isinstance(x, dict) and x.get("name") == episode_name), None)         if isinstance(items, list) else None
    if not episode:
        raise RuntimeError("generated podcast episode was not found")
    episode_id = episode.get("id")
    audio_url = episode.get("audio_url")
    if not isinstance(episode_id, str) or not isinstance(audio_url, str) or not audio_url.startswith("/"):
        raise RuntimeError("generated podcast has no bounded audio URL")
    raw, _ = request_bytes(base + audio_url, headers=headers, timeout=120, max_bytes=MAX_MEDIA)
    if len(raw) < 1000:
        raise RuntimeError("OpenNotebook podcast audio is unexpectedly small")
    audio = out / "podcast-teste.mp3"
    audio.write_bytes(raw)
    result = {
        "status": "PASS", "capability": "open-notebook.real-podcast",
        "authority": "UNTRUSTED", "outcome": "candidate",
        "job_id": job_id, "episode_id": episode_id, "episode_name": episode_name,
        "episode_profile": ep_names[0], "speaker_profile": sp_names[0],
        "file": audio.name, "bytes": len(raw), "sha256": sha256(raw),
        "note": "Real OpenNotebook generation. Human review is still required.",
    }
    write_json(out / "open-notebook-podcast.json", result)
    return result


def avatar(episode_id: str, avatar_name: str, out: Path) -> dict:
    if not avatar_name:
        raise NotConfigured("NEXUS_AVATAR_NAME is not configured")
    config = local_config()
    base, headers = config["base_url"], on_headers(config)
    path = "/api/podcasts/episodes/" + urllib.parse.quote(episode_id, safe="") + "/avatar"
    try:
        manifest, _ = request_json(
            base + path, method="POST",
            payload={"avatar": avatar_name, "device": "cuda", "batch_size": 8},
            headers=headers, timeout=960,
        )
    except RuntimeError as error:
        # CUDA can be absent on a test machine; retrying CPU is explicit and bounded.
        if "CUDA" not in str(error).upper():
            raise
        manifest, _ = request_json(
            base + path, method="POST",
            payload={"avatar": avatar_name, "device": "cpu", "batch_size": 4},
            headers=headers, timeout=960,
        )
    if not isinstance(manifest, dict) or manifest.get("authority") != "UNTRUSTED"             or manifest.get("outcome") != "candidate":
        raise RuntimeError("avatar result did not preserve candidate authority")
    job_id = manifest.get("job_id")
    if not isinstance(job_id, str) or len(job_id) != 64:
        raise RuntimeError("avatar job id invalid")
    raw, _ = request_bytes(
        base + "/api/podcasts/avatars/" + job_id + "/video",
        headers=headers, timeout=120, max_bytes=MAX_MEDIA,
    )
    if len(raw) < 1000 or b"ftyp" not in raw[:64]:
        raise RuntimeError("avatar MP4 invalid")
    video = out / "podcast-visual-teste.mp4"
    video.write_bytes(raw)
    result = {
        "status": "PASS", "capability": "open-notebook.real-avatar",
        "authority": "UNTRUSTED", "outcome": "candidate",
        "episode_id": episode_id, "job_id": job_id, "avatar": avatar_name,
        "file": video.name, "bytes": len(raw), "sha256": sha256(raw),
        "note": "Technical video validation only; lip-sync quality needs human review.",
    }
    write_json(out / "open-notebook-avatar.json", result)
    return result


COMMANDS = {
    "zotero": lambda a: zotero(a.query, a.output),
    "web": lambda a: internet_research(a.query, a.output),
    "music": lambda a: ace_music(a.output),
    "podcast": lambda a: podcast(a.output),
    "avatar": lambda a: avatar(a.episode_id, a.avatar_name, a.output),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--query", default="sistemas local-first conhecimento pessoal")
    parser.add_argument("--episode-id", default="")
    parser.add_argument("--avatar-name", default=os.environ.get("NEXUS_AVATAR_NAME", ""))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        result = COMMANDS[args.command](args)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except NotConfigured as error:
        value = {"status": "NOT_CONFIGURED", "capability": args.command, "error": str(error)}
        write_json(args.output / (args.command + "-not-configured.json"), value)
        print(json.dumps(value, ensure_ascii=False))
        return 2
    except Exception as error:
        value = {"status": "FAIL", "capability": args.command,
                 "error_type": type(error).__name__, "error": str(error)[:4000]}
        write_json(args.output / (args.command + "-failure.json"), value)
        print(json.dumps(value, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
