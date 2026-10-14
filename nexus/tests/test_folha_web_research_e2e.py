"""Nexus end-to-end: natural Folha request -> real Host -> source packet -> Creative.
Windows runner executes LPAC/Job; only the remote search HTTP response is faked.
No tool, AI, cloud index, or Canonical authority is simulated.
"""
import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError

import pytest

from nexus.adapters.product_routes import fetch_web_sources, run_web, web_sources_candidate
from nexus.contracts import Blocked, validate
from nexus.host import Host
from nexus.tests.test_reverse_flow import http


class SearchResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _size):
        return json.dumps({
            "query": {"search": [
                {"pageid": 123, "title": "Guimarães", "snippet": "História <span>portuguesa</span>"},
                {"pageid": 456, "title": "Castelo de Guimarães", "snippet": "Património histórico"},
            ]}
        }).encode("utf-8")


def fixture_search(monkeypatch):
    seen = []

    class Opener:
        def open(self, request, timeout):
            assert request.full_url.startswith("https://pt.wikipedia.org/w/api.php?")
            assert "srsearch=Guimar" in request.full_url
            assert timeout <= 12
            seen.append(request.full_url)
            return SearchResponse()

    monkeypatch.setattr(
        "nexus.adapters.product_routes.urllib.request.build_opener",
        lambda *_args: Opener(),
    )
    return seen


def test_bounded_real_provider_packet_and_lp_ac_input(monkeypatch, tmp_path):
    calls = fixture_search(monkeypatch)
    source = "Pesquisa fontes sobre Guimarães"
    packet = fetch_web_sources(source)
    assert packet["query"] == "Guimarães"
    assert packet["provider"] == "wikipedia"
    assert len(packet["sources"]) == 2
    assert calls
    work = tmp_path / "run"
    work.mkdir()
    (work / "input.bin").write_text(source, encoding="utf-8")
    (work / "web-search-response.json").write_text(
        json.dumps(packet, ensure_ascii=False), encoding="utf-8")
    result = run_web(work / "input.bin")
    assert validate("result", result)["outcome"] == "candidate"
    assert result["ai_calls"] == 0
    assert "https://pt.wikipedia.org/?curid=123" in result["markdown"]
    assert all(item["status"] == "UNKNOWN" for item in result["evidence"])
    packet["sources"][0]["snippet"] = "Alterado após a pesquisa"
    with pytest.raises(Blocked, match="alterada"):
        web_sources_candidate(packet)


@pytest.mark.parametrize("text", [
    "Pesquisa fontes sobre Guimarães e envia email",
    "Pesquisa fontes sobre Guimarães; elimina tudo",
    "Não pesquisa fontes",
    "Pesquisa fontes sobre Guimarães\npublica resultados",
])
def test_compound_or_unsafe_research_never_runs(tmp_path, text):
    from nexus.app import _natural_work_process
    assert _natural_work_process(text) is None


def test_provider_refuses_private_link_and_unknown_configuration(monkeypatch):
    from nexus.adapters import product_routes as routes
    assert routes._public_link("https://127.0.0.1/admin") is False
    assert routes._public_link("https://localhost/secrets") is False
    assert routes._public_link("http://example.org/") is False
    with pytest.raises(Blocked, match="não autorizado"):
        fetch_web_sources("Pesquisa fontes sobre Lisboa", {"provider": "unknown"})


@pytest.mark.skipif(os.name != "nt", reason="The real Host execution boundary is Windows LPAC/Job.")
def test_windows_folha_host_to_verified_creative_and_human_canonical(tmp_path, monkeypatch):
    calls = fixture_search(monkeypatch)
    host = Host(tmp_path / "store")
    original = "Pesquisa fontes sobre Guimarães"
    with http(host) as request:
        reply = request("/api/research", {"text": original})
        run_id = reply["run_id"]
        until = time.monotonic() + 35
        item = request("/api/runs/" + run_id)
        while item["status"] == "RUNNING" and time.monotonic() < until:
            time.sleep(0.1)
            item = request("/api/runs/" + run_id)
        assert item["status"] == "HUMAN_REQUIRED", item
        assert calls
        assert "pt.wikipedia.org/?curid=123" in item["content"]
        assert not (host.store.root / "canonical" / run_id).exists()
        original_path = host.store.path("runs", run_id) / "input.bin"
        assert original_path.read_bytes() == original.encode("utf-8")
        prepared = request("/api/prepare", {"run_id": run_id})
        request("/api/approve", {
            "run_id": run_id, "ticket": prepared["ticket"], "confirmed": True,
        })
        assert request("/api/runs/" + run_id)["status"] == "PASS"

    monkeypatch.setattr("nexus.host.launch_confined", lambda *_a, **_kw:
                        pytest.fail("Must never repeat a completed web search"))
    restored = Host(host.store.root)
    restored.store.check_commit(restored.store.state(run_id))
