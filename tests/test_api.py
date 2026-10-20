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

def test_ask_returns_answer_citations_and_sources(monkeypatch):
    from rag import generate
    from rag.llm import LLMResult
    monkeypatch.setattr(api, "search", lambda q, k: [Hit("d::p1::c0", "d.pdf", 1, "Refunds take ten days.", 0.9)])
    monkeypatch.setattr(generate, "complete", lambda s, u: LLMResult("Ten days [1].", 20, 4))
    r = client.post("/ask", json={"question": "How long do refunds take?"})
    body = r.json()
    assert r.status_code == 200 and body["answer"] == "Ten days [1]." and body["refused"] is False
    assert body["citations"][0]["doc"] == "d.pdf" and body["citations"][0]["page"] == 1
    assert body["retrieved"][0]["chunk_id"] == "d::p1::c0"


def test_ask_refuses_when_nothing_found(monkeypatch):
    monkeypatch.setattr(api, "search", lambda q, k: [])
    r = client.post("/ask", json={"question": "anything"})
    assert r.json()["refused"] is True and r.json()["citations"] == []


def test_ask_without_llm_key_is_a_clean_500(monkeypatch):
    from rag import generate
    from rag.llm import LLMConfigError
    monkeypatch.setattr(api, "search", lambda q, k: [Hit("c", "d", 1, "t", 0.9)])

    def no_key(s, u):
        raise LLMConfigError("ANTHROPIC_API_KEY is not set")
    monkeypatch.setattr(generate, "complete", no_key)
    r = client.post("/ask", json={"question": "q"})
    assert r.status_code == 500 and "ANTHROPIC" not in r.text


def test_ask_validation():
    assert client.post("/ask", json={"question": ""}).status_code == 422