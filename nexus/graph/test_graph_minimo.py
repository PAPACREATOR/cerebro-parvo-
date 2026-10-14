"""Deterministic, disposable graph tests. No Kernel/Host/Store mutations."""
import json
import sqlite3

import pytest

from nexus.graph.graph_minimo import GraphMinimo


def test_roundtrip_unicode_links_and_existing_edge_id(tmp_path):
    graph = GraphMinimo(tmp_path / "graph.sqlite")
    graph.criar_node("a", "nota", "Música e ciência")
    graph.criar_node("b", "fonte", "Fonte")
    first = graph.criar_edge("a", "b", "cita", {"origem": "órgão"})
    assert graph.criar_edge("a", "b", "cita") == first
    exported = graph.exportar_json()
    assert json.loads(exported)["nodes"][0]["titulo"] == "Música e ciência"
    assert json.loads(exported)["edges"][0]["id"] == first
    restored = GraphMinimo(tmp_path / "other.sqlite")
    restored.reconstruir_json(exported)
    assert json.loads(restored.exportar_json()) == json.loads(exported)
    assert restored.backlinks("b")[0]["origem_id"] == "a"
    assert restored.ligacoes("a")[0]["propriedades"] == {"origem": "órgão"}


@pytest.mark.parametrize("mutation", [
    lambda d: d.update(version=2),
    lambda d: d["nodes"].append(dict(d["nodes"][0])),
    lambda d: d["edges"][0].update(destino_id="missing"),
    lambda d: d["edges"][0].update(relacao="promovido_automaticamente"),
    lambda d: d["edges"].append(dict(d["edges"][0], id="different")),
    lambda d: d["nodes"][0].update(tipo=[]),
    lambda d: d["edges"][0].update(propriedades=[]),
    lambda d: d.update(admin=True),
])
def test_invalid_import_is_atomic(tmp_path, mutation):
    graph = GraphMinimo(tmp_path / "a.sqlite")
    graph.criar_node("a", "nota", "Nota")
    graph.criar_node("b", "fonte", "Fonte")
    graph.criar_edge("a", "b", "cita")
    original = graph.exportar_json()
    data = json.loads(original)
    mutation(data)
    with pytest.raises(ValueError):
        graph.reconstruir_json(data)
    assert graph.exportar_json() == original


@pytest.mark.parametrize("raw", [
    "{", '{"version":1,"version":1,"nodes":[],"edges":[]}',
    '{"version":1,"nodes":[],"edges":[],"invalid":NaN}',
    b"\xff", "x" * 8_000_001,
], ids=["syntax", "duplicate-keys", "nan", "invalid-utf8", "oversized"])
def test_invalid_json_is_rejected_without_state_change(tmp_path, raw):
    graph = GraphMinimo(tmp_path / "a.sqlite")
    graph.criar_node("a", "nota", "Original")
    previous = graph.exportar_json()
    with pytest.raises(ValueError):
        graph.reconstruir_json(raw)
    assert graph.exportar_json() == previous


def _snapshot(run, source, authority="canonical"):
    return {"run_id": run, "input_sha256": source,
            "content_sha256": "b" * 64, "authority": authority}


def test_derived_provenance_expansion_is_scoped_and_repeatable(tmp_path):
    graph = GraphMinimo(tmp_path / "graph.sqlite")
    a, b, c = "a" * 32, "b" * 32, "c" * 32
    snapshots = [_snapshot(a, "1" * 64), _snapshot(b, "1" * 64, "creative"),
                 _snapshot(c, "2" * 64)]
    graph.reconstruir_snapshots(snapshots)
    original = graph.exportar_json()
    graph.reconstruir_snapshots(snapshots)
    assert graph.exportar_json() == original
    assert graph.relacionados(a, {a, b, c}) == [b]
    assert graph.relacionados(a, {a, c}) == []
    assert graph.relacionados(b, {a, b}) == [a]
    assert graph.relacionados(a, {b, c}) == []
    assert graph.relacionados(a, {a, b}, limite=1) == [b]
    assert "creative" in original and "canonical" in original
    graph.reconstruir_snapshots([snapshots[0]])
    assert graph.relacionados(a, {a, b}) == []


@pytest.mark.parametrize("source", [
    [{"run_id": "not-uuid", "input_sha256": "1"*64,
      "content_sha256": "2"*64, "authority": "canonical"}],
    [{"run_id": "a"*32, "input_sha256": "bad",
      "content_sha256": "2"*64, "authority": "canonical"}],
    [{"run_id": "a"*32, "input_sha256": "1"*64,
      "content_sha256": "2"*64, "authority": "approved_without_gate"}],
])
def test_invalid_snapshots_keep_last_good_graph(tmp_path, source):
    graph = GraphMinimo(tmp_path / "graph.sqlite")
    graph.reconstruir_snapshots([_snapshot("a"*32, "1"*64)])
    original = graph.exportar_json()
    with pytest.raises(ValueError):
        graph.reconstruir_snapshots(source)
    assert graph.exportar_json() == original


def test_corrupted_database_does_not_touch_external_store(tmp_path):
    graph = GraphMinimo(tmp_path / "graph.sqlite")
    protected = tmp_path / "protected.md"
    protected.write_bytes(b"unaltered")
    graph.criar_node("a", "nota", "ok")
    with pytest.raises(sqlite3.Error):
        with graph._connect() as con:
            con.execute("DROP TABLE nodes")
            con.execute("SELECT * FROM nodes")
    assert protected.read_bytes() == b"unaltered"
