import numpy as np
import pytest
from qdrant_client import QdrantClient

from rag.store import index_chunks, point_id

CHUNKS = [{"chunk_id": f"d::p1::c{i}", "doc": "d", "page": 1, "text": f"text {i}"} for i in range(3)]
VECS = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.7, 0.7, 0.0]])


def test_point_id_is_stable_and_unique():
    assert point_id("a::p1::c0") == point_id("a::p1::c0")
    assert point_id("a::p1::c0") != point_id("a::p1::c1")


def test_index_counts_and_is_repeatable():
    client = QdrantClient(":memory:")
    assert index_chunks(client, "t", CHUNKS, VECS) == 3
    assert index_chunks(client, "t", CHUNKS, VECS) == 3          # rebuilding does not duplicate


def test_mismatched_lengths_rejected():
    with pytest.raises(ValueError):
        index_chunks(QdrantClient(":memory:"), "t", CHUNKS, VECS[:2])