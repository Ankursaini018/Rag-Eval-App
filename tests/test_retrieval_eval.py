import numpy as np
import pytest
from qdrant_client import QdrantClient

from rag.retrieval_eval import evaluate_retriever, format_table
from rag.retrievers import VectorRetriever, build_retriever
from rag.search import Hit
from rag.store import index_chunks


class FakeRetriever:
    """Returns a pre-set ranking of pages for each question text."""
    name = "fake"

    def __init__(self, rankings):
        self.rankings = rankings

    def retrieve(self, query, k):
        return [Hit(f"{d}::p{p}::c0", d, p, "t", 1.0) for d, p in self.rankings[query][:k]]


def entry(qid, question, gold, type="single_fact"):
    return {"id": qid, "question": question, "type": type,
            "answer": None if not gold else "a", "gold": [{"doc": d, "page": p} for d, p in gold]}


ENTRIES = [
    entry("q001", "found first", [("a", 1)]),
    entry("q002", "found second", [("a", 2)]),
    entry("q003", "never found", [("a", 3)]),
    entry("q004", "two pages, one found", [("a", 1), ("b", 1)], type="multi_chunk"),
    entry("q005", "no answer exists", [], type="unanswerable"),
]
RANKINGS = {
    "found first": [("a", 1), ("x", 1), ("x", 2)],
    "found second": [("x", 1), ("a", 2), ("x", 2)],
    "never found": [("x", 1), ("x", 2), ("x", 3)],
    "two pages, one found": [("a", 1), ("x", 1), ("x", 2)],
}


def test_evaluate_known_numbers():
    result = evaluate_retriever(FakeRetriever(RANKINGS), ENTRIES)
    s = result["summary"]
    assert s["n"] == 4 and result["skipped_unanswerable"] == 1
    assert s["recall@1"] == pytest.approx((1 + 0 + 0 + 0.5) / 4)
    assert s["recall@3"] == pytest.approx((1 + 1 + 0 + 0.5) / 4)
    assert s["mrr"] == pytest.approx((1 + 0.5 + 0 + 1) / 4)
    assert result["by_type"]["multi_chunk"]["recall@5"] == 0.5
    assert result["by_type"]["single_fact"]["n"] == 3


def test_format_table_has_all_and_per_type_rows():
    table = format_table(evaluate_retriever(FakeRetriever(RANKINGS), ENTRIES))
    assert "recall@1" in table and "MRR" in table
    assert "**all**" in table and "| multi_chunk | 1 |" in table


def test_vector_retriever_works_end_to_end_with_in_memory_qdrant():
    chunks = [{"chunk_id": "a::p1::c0", "doc": "a", "page": 1, "text": "alpha"},
              {"chunk_id": "a::p2::c0", "doc": "a", "page": 2, "text": "beta"}]
    qdrant = QdrantClient(":memory:")
    index_chunks(qdrant, "t", chunks, np.array([[1.0, 0.0], [0.0, 1.0]]))
    retriever = VectorRetriever("t", client=qdrant, embed=lambda q: [0.0, 1.0] if "beta" in q else [1.0, 0.0])
    entries = [entry("q001", "about alpha", [("a", 1)]), entry("q002", "about beta", [("a", 2)])]
    s = evaluate_retriever(retriever, entries)["summary"]
    assert s["recall@1"] == 1.0 and s["mrr"] == 1.0


def test_unknown_retriever_name_is_a_clear_error():
    with pytest.raises(ValueError, match="unknown retriever"):
        build_retriever("magic")