import pytest

from rag.metrics import mean, recall_at_k, reciprocal_rank

A, B, C, D = ("d.pdf", 1), ("d.pdf", 2), ("d.pdf", 3), ("e.pdf", 1)


def test_recall_single_gold_page():
    ranking = [A, B, C, D]
    assert recall_at_k(ranking, [C], 1) == 0.0
    assert recall_at_k(ranking, [C], 3) == 1.0
    assert recall_at_k(ranking, [C], 5) == 1.0
    assert recall_at_k(ranking, [("zzz", 9)], 5) == 0.0


def test_recall_two_gold_pages_gives_partial_credit():
    ranking = [A, D, B, C]
    assert recall_at_k(ranking, [A, C], 1) == 0.5
    assert recall_at_k(ranking, [A, C], 3) == 0.5
    assert recall_at_k(ranking, [A, C], 4) == 1.0


def test_two_chunks_from_the_same_page_do_not_count_twice():
    assert recall_at_k([A, A, B], [A, B], 2) == 0.5


def test_recall_with_fewer_results_than_k():
    assert recall_at_k([A], [A], 5) == 1.0
    assert recall_at_k([], [A], 5) == 0.0


def test_recall_rejects_bad_input():
    with pytest.raises(ValueError):
        recall_at_k([A], [], 3)
    with pytest.raises(ValueError):
        recall_at_k([A], [A], 0)


def test_reciprocal_rank_positions():
    assert reciprocal_rank([A, B, C], [A]) == 1.0
    assert reciprocal_rank([A, B, C], [B]) == 0.5
    assert reciprocal_rank([A, B, C], [C]) == pytest.approx(1 / 3)
    assert reciprocal_rank([A, B, C], [D]) == 0.0
    assert reciprocal_rank([], [A]) == 0.0


def test_reciprocal_rank_uses_the_first_gold_page_found():
    assert reciprocal_rank([D, B, A], [A, B]) == 0.5
    with pytest.raises(ValueError):
        reciprocal_rank([A], [])


def test_mrr_is_the_mean_of_reciprocal_ranks():
    assert mean([1.0, 0.5, 0.0]) == pytest.approx(0.5)
    assert mean([]) == 0.0