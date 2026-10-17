import numpy as np
from qdrant_client import QdrantClient

from rag.search import Hit, search
from rag.store import index_chunks

CHUNKS = [{"chunk_id": f"d::p{i}::c0", "doc": "d", "page": i, "text": f"text {i}"} for i in (1, 2, 3)]
VECS = np.array([[1.0, 0.0], [0.0, 1.0], [0.6, 0.8]])


def make_client():
    c = QdrantClient(":memory:")
    index_chunks(c, "t", CHUNKS, VECS)
    return c


def test_search_orders_by_similarity_and_returns_hits():
    hits = search("q", k=3, collection="t", client=make_client(), embed=lambda q: np.array([0.0, 1.0]))
    assert [h.page for h in hits] == [2, 3, 1]
    assert isinstance(hits[0], Hit) and hits[0].score > hits[1].score > hits[2].score
    assert hits[0].text == "text 2" and hits[0].chunk_id == "d::p2::c0"


def test_k_limits_results():
    hits = search("q", k=1, collection="t", client=make_client(), embed=lambda q: np.array([1.0, 0.0]))
    assert len(hits) == 1 and hits[0].page == 1