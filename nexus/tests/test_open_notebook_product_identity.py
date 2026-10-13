"""OpenNotebook product-plan identity is evidence, not authority.

Test the actual HTTP preparation adapter with an in-memory HTTP peer. No
OpenNotebook backend, Windows credentials, Host, Store or Canonical are changed.
"""
import io
import json

import pytest

from nexus.adapters import product_routes
from nexus.contracts import Blocked


CONFIG = {
    "base_url": "http://127.0.0.1:5055",
    "password": "local-test-only",
    "model_id": "model:expected",
    "transformation_id": "transformation:expected",
}
SOURCE = "Coimbra recebeu vinte caixas."
ROUTES = ("video", "podcast", "visual_podcast")


def _response():
    return {
        "output": json.dumps({
            "title": "Resumo",
            "body": "Plano candidato sem autorização.",
            "steps": ["Escrever guião", "Rever fontes"],
            "quotes": [SOURCE],
        }),
        "model_id": CONFIG["model_id"],
        "transformation_id": CONFIG["transformation_id"],
    }


class _HTTPReply:
    def __init__(self, data):
        self.stream = io.BytesIO(json.dumps(data).encode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, n=-1):
        return self.stream.read(n)


def _peer(monkeypatch, response):
    calls = []

    class Opener:
        def open(self, request, timeout):
            calls.append((request, timeout))
            return _HTTPReply(response)

    monkeypatch.setattr(product_routes.urllib.request, "build_opener", lambda *_: Opener())
    return calls


@pytest.mark.parametrize("route", ROUTES)
def test_matching_product_identity_preserves_actual_evidence(monkeypatch, route):
    calls = _peer(monkeypatch, _response())
    actual = product_routes.fetch_plan(SOURCE, route, CONFIG)
    assert actual == _response()
    assert len(calls) == 1
    request, timeout = calls[0]
    payload = json.loads(request.data)
    assert payload == {
        "model_id": CONFIG["model_id"],
        "transformation_id": CONFIG["transformation_id"],
        "input_text": f"ROUTE: {route}\n\nSOURCE:\n{SOURCE}",
    }
    assert timeout == 180
    result = product_routes.normalize_plan(
        actual["output"], SOURCE, route, actual["model_id"], actual["transformation_id"]
    )
    assert result["outcome"] == "candidate"
    assert result["status"] == "UNKNOWN"
    evidence = json.loads(result["evidence"][0]["value"])
    assert evidence["model_id"] == CONFIG["model_id"]
    assert evidence["transformation_id"] == CONFIG["transformation_id"]


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("change", (
    {"model_id": "model:different"},
    {"transformation_id": "transformation:different"},
    {"model_id": None},
    {"transformation_id": 123},
    {"unexpected_authority": "canonical"},
))
def test_product_plan_rejects_identity_or_contract_mismatch(monkeypatch, route, change):
    response = {**_response(), **change}
    calls = _peer(monkeypatch, response)
    with pytest.raises(Blocked):
        product_routes.fetch_plan(SOURCE, route, CONFIG)
    assert len(calls) == 1


@pytest.mark.parametrize("missing", ("model_id", "transformation_id"))
def test_product_plan_rejects_identity_omission(monkeypatch, missing):
    response = _response()
    response.pop(missing)
    calls = _peer(monkeypatch, response)
    with pytest.raises(Blocked):
        product_routes.fetch_plan(SOURCE, "podcast", CONFIG)
    assert len(calls) == 1


def test_product_plan_rejects_non_object_envelope(monkeypatch):
    calls = _peer(monkeypatch, [_response()])
    with pytest.raises(Blocked):
        product_routes.fetch_plan(SOURCE, "podcast", CONFIG)
    assert len(calls) == 1
