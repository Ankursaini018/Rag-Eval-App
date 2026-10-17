from fastapi.testclient import TestClient

from rag import api
from rag.search import Hit

client = TestClient(api.app)


def test_search_endpoint_returns_hits(monkeypatch):
    monkeypatch.setattr(api, "search", lambda q, k: [Hit("d::p1::c0", "d", 1, "hello", 0.9)])
    r = client.post("/search", json={"query": "hi", "k": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["hits"][0] == {"chunk_id": "d::p1::c0", "doc": "d", "page": 1, "text": "hello", "score": 0.9}


def test_validation_errors():
    assert client.post("/search", json={"query": ""}).status_code == 422
    assert client.post("/search", json={"query": "x", "k": 0}).status_code == 422
    assert client.post("/search", json={"query": "x", "k": 99}).status_code == 422


def test_backend_down_gives_503_without_details(monkeypatch):
    def boom(q, k):
        raise ConnectionError("secret-host:6333 refused")
    monkeypatch.setattr(api, "search", boom)
    r = client.post("/search", json={"query": "x"})
    assert r.status_code == 503 and "secret-host" not in r.text