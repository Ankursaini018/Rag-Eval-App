"""Vector search: question in, the closest chunks (with scores) out."""
from dataclasses import asdict, dataclass

from .embed import embed_query
from .store import DEFAULT_COLLECTION, get_client


@dataclass
class Hit:
    chunk_id: str
    doc: str
    page: int
    text: str
    score: float        # cosine similarity, higher = closer in meaning (max 1.0)

    def to_dict(self) -> dict:
        return asdict(self)


def search(query: str, k: int = 5, collection: str | None = None, client=None, embed=embed_query) -> list[Hit]:
    """Embed the query, ask Qdrant for the k nearest chunks. `client` and `embed` can be swapped in tests."""
    client = client or get_client()
    result = client.query_points(
        collection_name=collection or DEFAULT_COLLECTION,
        query=[float(x) for x in embed(query)],
        limit=k,
        with_payload=True,
    )
    hits = []
    for point in result.points:
        p = point.payload or {}
        hits.append(Hit(p["chunk_id"], p["doc"], p["page"], p["text"], float(point.score)))
    return hits