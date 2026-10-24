"""One interface for every way of finding chunks, so the eval code never needs to know which one it tests.

A retriever is anything with a `name` and a `retrieve(query, k)` method that returns a list of Hit
(best first). Today: VectorRetriever. Later: BM25, hybrid, reranked, with query rewriting.
"""
from typing import Protocol

from .search import Hit, search


class Retriever(Protocol):
    name: str

    def retrieve(self, query: str, k: int) -> list[Hit]: ...


class VectorRetriever:
    """Dense retrieval: embed the query, find the nearest chunk vectors in Qdrant (what /search does)."""

    def __init__(self, collection: str | None = None, client=None, embed=None):
        self.collection = collection
        self.client = client
        self.embed = embed
        self.name = f"vector[{collection or 'default'}]"

    def retrieve(self, query: str, k: int) -> list[Hit]:
        kwargs = {"collection": self.collection, "client": self.client}
        if self.embed is not None:
            kwargs["embed"] = self.embed
        return search(query, k, **kwargs)


def build_retriever(kind: str, collection: str | None = None) -> Retriever:
    """Create a retriever by name. Later days register more kinds here."""
    if kind == "vector":
        return VectorRetriever(collection=collection)
    raise ValueError(f"unknown retriever '{kind}'. Available: vector")