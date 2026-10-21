"""Smoke test: the WHOLE /ask path in one go, with nothing external.
Real code runs for: HTTP layer -> search -> Qdrant (in memory) -> prompt -> citation parsing.
Only two things are faked: the embedding model (tiny hand-made vectors) and the LLM."""
import numpy as np
import pytest
from qdrant_client import QdrantClient
from fastapi.testclient import TestClient

from rag import api, generate
from rag.llm import LLMResult
from rag.prompts import REFUSAL
from rag.search import search
from rag.store import index_chunks

CHUNKS = [
    {"chunk_id": "guide.pdf::p1::c0", "doc": "guide.pdf", "page": 1, "text": "Refunds take ten days."},
    {"chunk_id": "guide.pdf::p2::c0", "doc": "guide.pdf", "page": 2, "text": "Support is open on weekdays."},
]
VECTORS = np.array([[1.0, 0.0], [0.0, 1.0]])   # chunk 0 points "right", chunk 1 points "up"


def fake_embed(text: str):
    return [1.0, 0.0] if "refund" in text.lower() else [0.0, 1.0]


@pytest.fixture
def client(monkeypatch):
    qdrant = QdrantClient(":memory:")
    index_chunks(qdrant, "smoke", CHUNKS, VECTORS)
    monkeypatch.setattr(api, "search",
                        lambda q, k: search(q, k, collection="smoke", client=qdrant, embed=fake_embed))
    return TestClient(api.app)


def test_ask_end_to_end(client, monkeypatch):
    seen = {}

    def fake_complete(system, user):
        seen["user"] = user
        return LLMResult("Refunds take ten days [1].", 30, 6)

    monkeypatch.setattr(generate, "complete", fake_complete)
    body = client.post("/ask", json={"question": "How long do refunds take?"}).json()
    assert body["refused"] is False
    assert body["retrieved"][0]["chunk_id"] == "guide.pdf::p1::c0"   # the right chunk ranked first
    assert "Refunds take ten days." in seen["user"]                  # and it reached the prompt
    assert body["citations"] == [{"n": 1, "chunk_id": "guide.pdf::p1::c0", "doc": "guide.pdf",
                                  "page": 1, "text": "Refunds take ten days."}]


def test_ask_refusal_end_to_end(client, monkeypatch):
    monkeypatch.setattr(generate, "complete", lambda s, u: LLMResult(REFUSAL, 30, 8))
    body = client.post("/ask", json={"question": "What is the capital of France?"}).json()
    assert body["refused"] is True and body["citations"] == []