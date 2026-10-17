"""Turn text into embeddings (lists of numbers that capture meaning) with a BAAI bge model."""
import hashlib
from pathlib import Path

import numpy as np

MODEL_NAME = "BAAI/bge-small-en-v1.5"  # small, fast on CPU, 384-dimensional vectors
# bge models are trained so that a SEARCH QUERY gets this instruction in front of it.
# Documents/snippets get no prefix.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model = None


def get_model():
    """Load the model once (first call downloads ~130 MB, later calls reuse the local copy)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # imported here so tests don't need it
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    """Embed documents. Returns an array of shape (len(texts), 384).
    normalize_embeddings=True scales every vector to length 1."""
    vecs = get_model().encode(texts, batch_size=batch_size, normalize_embeddings=True,
                              show_progress_bar=len(texts) > 50)
    return np.asarray(vecs, dtype=np.float32)


def embed_query(query: str) -> np.ndarray:
    """Embed a search query (adds the bge query prefix). Returns shape (384,)."""
    return embed_texts([QUERY_PREFIX + query])[0]


def embed_cached(texts: list[str], cache_path: str | Path) -> np.ndarray:
    """Embed texts, but reuse a saved copy if the texts and the model have not changed.
    The cache key is a hash of the model name + all texts, so editing a snippet re-embeds."""
    key = hashlib.sha256((MODEL_NAME + "\n" + "\n".join(texts)).encode()).hexdigest()
    path = Path(cache_path)
    if path.exists():
        saved = np.load(path, allow_pickle=False)
        if str(saved["key"]) == key:
            return saved["vectors"]
    vectors = embed_texts(texts)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, key=key, vectors=vectors)
    return vectors

def embed_chunks(chunks: list[dict], batch_size: int = 64) -> np.ndarray:
    """Embed the text of every chunk, in batches. Row i of the result belongs to chunks[i].

    Batching = sending 64 chunks through the model at once. It is much faster than one at a time
    (the model does the maths for all 64 together) while keeping memory use small."""
    if not chunks:
        return np.zeros((0, 384), dtype=np.float32)
    vectors = embed_texts([c["text"] for c in chunks], batch_size=batch_size)
    assert len(vectors) == len(chunks), "one vector per chunk"
    return vectors