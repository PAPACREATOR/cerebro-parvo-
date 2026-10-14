"""Cross-platform HTTP+Host+Store+FTS5 behavioural regression."""
from nexus.host import Host
from nexus.tests.test_memory_search_http import stored, search
from nexus.tests.test_reverse_flow import http


def test_natural_search_roundtrip_with_accents_prefix_and_restart(tmp_path):
    root = tmp_path / "memory"
    host = Host(root)
    phrase = stored(host, "História Guimarães: arquivo histórico português.", approved=True)
    separated = stored(host, "História medieval portuguesa e documentos. Guimarães.", approved=True)
    with http(host) as call:
        ids = [r["run_id"] for r in search(call, query="história Guimarães")["results"]]
        assert ids == [phrase, separated]
        for expression in ("Guimarães", "Guimaraes", "Guimarae"):
            assert {r["run_id"] for r in search(call, query=expression)["results"]} == {
                phrase, separated
            }
    restored = Host(root)
    with http(restored) as call:
        assert [r["run_id"] for r in search(call, query="história Guimarães")["results"]] == [
            phrase, separated
        ]


def test_natural_expansion_respects_creative_scope_and_literal_queries(tmp_path):
    host = Host(tmp_path / "memory")
    draft = stored(host, "Guimarães: rascunho reservado", approved=False)
    approved = stored(host, "nexusterm resultado consolidado", approved=True)
    with http(host) as call:
        assert search(call, query="Guimarae")["results"] == []
        assert [r["run_id"] for r in search(
            call, query="Guimarae", include_creative=True)["results"]] == [draft]
        assert [r["run_id"] for r in search(call, query="nexusterm")["results"]] == [
            approved
        ]
        for literal in ("nexusterm OR sensitive", '" OR nexusterm', "*",
                        "'; DROP TABLE docs;--"):
            assert search(call, query=literal)["results"] == []
    assert not host.store.path("canonical", draft).exists()
