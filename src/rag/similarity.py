"""Cosine similarity written by hand with numpy (no library doing the maths for us)."""
import numpy as np


def cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Similarity between one query vector (d,) and many vectors (n, d). Returns (n,) in [-1, 1].

    cosine(a, b) = (a . b) / (|a| * |b|)
    1 = same direction (same meaning), 0 = unrelated, -1 = opposite.
    """
    q = np.asarray(query, dtype=float)
    m = np.asarray(matrix, dtype=float)
    dots = m @ q                                          # a . b for every row at once
    norms = np.linalg.norm(m, axis=1) * np.linalg.norm(q)  # |a| * |b|
    return dots / np.maximum(norms, 1e-12)                # guard against dividing by zero


def top_k(query: np.ndarray, matrix: np.ndarray, k: int = 3) -> list[tuple[int, float]]:
    """Indices and scores of the k most similar rows, best first."""
    sims = cosine_similarity(query, matrix)
    order = np.argsort(-sims)[:k]
    return [(int(i), float(sims[i])) for i in order]