from __future__ import annotations

import json
from pathlib import Path
import urllib.parse

import pytest

from nexus.windows import real_acceptance as acceptance


def test_zotero_search_is_read_only_and_compacts_results(tmp_path, monkeypatch):
    calls = []

    def fake_bytes(url, **kwargs):
        calls.append(("bytes", url, kwargs))
        return b"{}", {"zotero-server-id": "local-test"}

    def fake_json(url, **kwargs):
        calls.append(("json", url, kwargs))
        return [
            {"data": {"key": "A1", "itemType": "book", "title": "Livro A", "date": "2026"}},
            {"data": {"key": "B2", "itemType": "article", "title": "Artigo B", "date": "2025"}},
        ], {"zotero-server-id": "local-test"}

    monkeypatch.setattr(acceptance, "request_bytes", fake_bytes)
    monkeypatch.setattr(acceptance, "request_json", fake_json)

    result = acceptance.zotero("memória local", tmp_path)

    assert result["status"] == "PASS"
    assert result["authority"] == "NONE"
    assert result["matches"] == 2
    assert all(call[2].get("method", "GET") == "GET" for call in calls)
    assert all("payload" not in call[2] for call in calls)
    query = urllib.parse.urlsplit(calls[1][1]).query
    params = urllib.parse.parse_qs(query)
    assert params["q"] == ["memória local"]
    assert params["qmode"] == ["everything"]
    assert json.loads((tmp_path / "zotero-search.json").read_text("utf-8"))["items"][0]["key"] == "A1"


def test_zotero_invalid_item_envelope_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(acceptance, "request_bytes", lambda *a, **k: (b"{}", {}))
    monkeypatch.setattr(acceptance, "request_json", lambda *a, **k: ({"not": "a list"}, {}))
    with pytest.raises(RuntimeError, match="not a list"):
        acceptance.zotero("x", tmp_path)


def test_internet_research_persists_only_bounded_results(tmp_path, monkeypatch):
    rows = [{"title": f"Tema {i}", "pageid": i} for i in range(10)]
    monkeypatch.setattr(
        acceptance, "request_json",
        lambda *a, **k: ({"query": {"search": rows}}, {}),
    )
    result = acceptance.internet_research("teste", tmp_path)
    assert result["status"] == "PASS"
    assert result["authority"] == "NONE"
    assert len(result["results"]) == 5
    assert all(item["url"].startswith("https://pt.wikipedia.org/wiki/") for item in result["results"])


def test_internet_research_rejects_invalid_search_shape(tmp_path, monkeypatch):
    monkeypatch.setattr(
        acceptance, "request_json",
        lambda *a, **k: ({"query": {"search": "wrong"}}, {}),
    )
    with pytest.raises(RuntimeError, match="invalid"):
        acceptance.internet_research("teste", tmp_path)


def test_ace_music_allows_lazy_model_initialization_but_still_obeys_job_failure(tmp_path, monkeypatch):
    responses = iter([
        ({"data": {"status": "ok", "models_initialized": False}}, {}),
        ({"code": 200, "data": {"task_id": "task-lazy"}}, {}),
        ({"data": [{"status": 2, "result": ""}]}, {}),
    ])
    monkeypatch.setattr(acceptance, "request_json", lambda *a, **k: next(responses))
    with pytest.raises(RuntimeError, match="reported failure"):
        acceptance.ace_music(tmp_path)


def test_ace_music_failed_job_never_downloads_audio(tmp_path, monkeypatch):
    responses = iter([
        ({"data": {"status": "ok", "models_initialized": True}}, {}),
        ({"code": 200, "data": {"task_id": "task-1"}}, {}),
        ({"data": [{"status": 2, "result": ""}]}, {}),
    ])
    monkeypatch.setattr(acceptance, "request_json", lambda *a, **k: next(responses))

    def forbidden(*_args, **_kwargs):
        pytest.fail("failed ACE task must not download audio")

    monkeypatch.setattr(acceptance, "request_bytes", forbidden)
    with pytest.raises(RuntimeError, match="reported failure"):
        acceptance.ace_music(tmp_path)
    assert not (tmp_path / "musica-teste.mp3").exists()


def test_podcast_requires_configured_profiles(tmp_path, monkeypatch):
    monkeypatch.setattr(
        acceptance, "local_config",
        lambda: {"base_url": "http://127.0.0.1:5055", "password": "x"},
    )

    def fake_json(url, **_kwargs):
        if url.endswith("/openapi.json"):
            return {
                "paths": {
                    "/api/episode-profiles": {"get": {}},
                    "/api/speaker-profiles": {"get": {}},
                }
            }, {}
        return [], {}

    monkeypatch.setattr(acceptance, "request_json", fake_json)
    with pytest.raises(acceptance.NotConfigured, match="profiles"):
        acceptance.podcast(tmp_path)


def test_avatar_without_operator_portrait_is_not_configured(tmp_path):
    with pytest.raises(acceptance.NotConfigured, match="NEXUS_AVATAR_NAME"):
        acceptance.avatar("episode:1", "", tmp_path)


def test_output_failures_leave_no_media_candidate(tmp_path, monkeypatch):
    monkeypatch.setattr(
        acceptance, "request_json",
        lambda *a, **k: ({"data": {"status": "bad", "models_initialized": True}}, {}),
    )
    with pytest.raises(acceptance.NotConfigured):
        acceptance.ace_music(tmp_path)
    assert not list(tmp_path.glob("*.mp3"))
    assert not list(tmp_path.glob("*.mp4"))


def test_commands_are_explicit_and_do_not_include_canonical_mutation():
    assert set(acceptance.COMMANDS) == {"book", "zotero", "web", "music", "podcast", "avatar"}
    source = Path(acceptance.__file__).read_text("utf-8")
    assert "from nexus.store" not in source
    assert "Store(" not in source
