"""Full authenticated FTS5 -> verified graph -> Folha backend tests."""
import sqlite3
from urllib.error import HTTPError

import pytest

from nexus.host import Host
from nexus.tests.test_memory_search_http import search, stored
from nexus.tests.test_reverse_flow import http


def test_fts5_expands_verified_source_without_exposing_creative(tmp_path):
    host = Host(tmp_path / "memory")
    matching = stored(host, "nexusterm texto aprovado de pesquisa", approved=True)
    related = stored(host, "documento diferente da mesma entrada", approved=True)
    private = stored(host, "hipótese privada ligada", approved=False)
    with http(host) as call:
        public = search(call)
        assert [r["run_id"] for r in public["results"]] == [matching]
        links = public["results"][0]["related"]
        assert len(links) == 1
        assert links[0]["authority"] == "canonical"
        assert "documento diferente" in links[0]["snippet"]
        assert all("privada" not in str(r) for r in public["results"])
        combined = search(call, include_creative=True)
        links = combined["results"][0]["related"]
        assert len(links) == 2
        assert {r["authority"] for r in links} == {"canonical", "creative"}
        assert any("hipótese privada" in r["snippet"] for r in links)
        assert host.store.state(private)["status"] == "HUMAN_REQUIRED"
        assert host.store.state(related)["status"] == "PASS"
    assert not host.store.path("canonical", private).exists()


def test_approval_rebuilds_derived_relations_without_automatic_promotion(tmp_path):
    host = Host(tmp_path / "memory")
    matching = stored(host, "nexusterm documento aprovado", approved=True)
    draft = stored(host, "documento para revisão humana", approved=False)
    with http(host) as call:
        assert search(call)["results"][0]["related"] == []
        assert len(search(call, include_creative=True)["results"][0]["related"]) == 1
        assert search(call)["results"][0]["related"] == []
        ticket = call("/api/prepare", {"run_id": draft})
        with pytest.raises(HTTPError):
            call("/api/approve", {"run_id": draft, "ticket": ticket["ticket"],
                                  "confirmed": False})
        assert search(call)["results"][0]["related"] == []
        new_ticket = call("/api/prepare", {"run_id": draft})
        approved = call("/api/approve", {"run_id": draft, "ticket": new_ticket["ticket"],
                                        "confirmed": True})
        assert approved["status"] == "PASS"
        answer = search(call)["results"][0]
        assert len(answer["related"]) == 1
        assert answer["related"][0]["authority"] == "canonical"
        assert "revisão humana" in answer["related"][0]["snippet"]
        assert answer["run_id"] == matching


def test_invalid_payload_and_wrong_session_never_read_graph(tmp_path):
    host = Host(tmp_path / "memory")
    stored(host, "nexusterm trabalho verificado", approved=True)
    graph_db = tmp_path / "memory-fts5-index" / "graph.sqlite"
    with http(host) as call:
        with pytest.raises(HTTPError) as error:
            search(call, session="invalid")
        assert error.value.code == 403
        with pytest.raises(HTTPError) as error:
            call("/api/search", {"query": "nexusterm", "include_creative": True,
                                 "limit": 8, "approval": "auto"})
        assert error.value.code == 403
        assert not graph_db.exists()
        assert search(call)["results"]
        assert graph_db.exists()


def test_relations_are_rebuilt_from_store_on_restart(tmp_path):
    host = Host(tmp_path / "memory")
    stored(host, "nexusterm documento um", approved=True)
    stored(host, "outro documento", approved=True)
    with http(host) as call:
        assert len(search(call)["results"][0]["related"]) == 1
    graph_db = tmp_path / "memory-fts5-index" / "graph.sqlite"
    with sqlite3.connect(graph_db) as db:
        db.execute("DELETE FROM edges")
    restarted = Host(tmp_path / "memory")
    with http(restarted) as call:
        assert len(search(call)["results"][0]["related"]) == 1
