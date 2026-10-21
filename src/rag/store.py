"""Qdrant (the vector database): create a collection, load chunks, run searches."""
import uuid
from functools import lru_cache

from qdrant_client import QdrantClient, models

from .config import COLLECTION as DEFAULT_COLLECTION  # noqa: F401
from .config import QDRANT_API_KEY, QDRANT_URL


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    if QDRANT_URL == ":memory:":
        return QdrantClient(":memory:")
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=30)


def point_id(chunk_id: str) -> str:
    """Qdrant ids must be integers or UUIDs. A UUID made FROM the chunk id is always the same for
    the same chunk, so loading twice overwrites instead of creating duplicates."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def recreate_collection(client: QdrantClient, name: str, dim: int) -> None:
    """A collection is like a table. Cosine distance matches how we compare embeddings."""
    if client.collection_exists(name):
        client.delete_collection(name)
    client.create_collection(
        collection_name=name,
        vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
    )


def upsert_chunks(client: QdrantClient, name: str, chunks: list[dict], vectors, batch_size: int = 64) -> None:
    """Upsert = insert, or overwrite if the id exists. Each point = vector + the chunk itself (payload)."""
    for i in range(0, len(chunks), batch_size):
        points = [
            models.PointStruct(id=point_id(c["chunk_id"]), vector=[float(x) for x in v], payload=c)
            for c, v in zip(chunks[i:i + batch_size], vectors[i:i + batch_size])
        ]
        client.upsert(collection_name=name, points=points)


def index_chunks(client: QdrantClient, name: str, chunks: list[dict], vectors) -> int:
    """Rebuild a collection from scratch and return how many points it now holds."""
    if len(chunks) != len(vectors):
        raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
    recreate_collection(client, name, len(vectors[0]))
    upsert_chunks(client, name, chunks, vectors)
    return client.count(collection_name=name, exact=True).count