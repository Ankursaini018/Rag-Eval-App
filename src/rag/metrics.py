"""Retrieval metrics. They compare the PAGES of the retrieved chunks with the gold pages of a question.

`retrieved` is the ranked list of (doc, page) pairs, best first, one per retrieved chunk
(so the same page can appear twice if two of its chunks were retrieved).
`gold` is the set of (doc, page) pairs that contain the answer.
"""
from typing import Iterable

Page = tuple[str, int]


def recall_at_k(retrieved: list[Page], gold: Iterable[Page], k: int) -> float:
    """Of the gold pages, what fraction appears in the top k results?
    One gold page: 1.0 (found) or 0.0 (missed). Two gold pages with one found: 0.5."""
    gold = set(gold)
    if not gold:
        raise ValueError("recall is undefined without gold pages (skip unanswerable questions)")
    if k < 1:
        raise ValueError("k must be at least 1")
    found = gold & set(retrieved[:k])
    return len(found) / len(gold)