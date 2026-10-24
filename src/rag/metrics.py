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



def reciprocal_rank(retrieved: list[Page], gold: Iterable[Page]) -> float:
    """1 / (position of the FIRST result that is a gold page). Position 1 -> 1.0, 2 -> 0.5, 3 -> 0.33...
    0.0 if no gold page is in the list."""
    gold = set(gold)
    if not gold:
        raise ValueError("reciprocal rank is undefined without gold pages (skip unanswerable questions)")
    for position, page in enumerate(retrieved, start=1):
        if page in gold:
            return 1.0 / position
    return 0.0


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0