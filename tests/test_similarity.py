import numpy as np

from rag.similarity import cosine_similarity, top_k


def test_identical_orthogonal_opposite():
    q = np.array([1.0, 0.0])
    m = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]])
    assert np.allclose(cosine_similarity(q, m), [1.0, 0.0, -1.0])


def test_length_does_not_matter():
    q = np.array([1.0, 2.0, 3.0])
    assert np.allclose(cosine_similarity(q, np.array([q * 10])), [1.0])


def test_zero_vector_does_not_crash():
    assert np.allclose(cosine_similarity(np.array([1.0, 0.0]), np.array([[0.0, 0.0]])), [0.0])


def test_top_k_order():
    q = np.array([1.0, 0.0])
    m = np.array([[0.0, 1.0], [1.0, 0.1], [1.0, 0.0]])
    assert [i for i, _ in top_k(q, m, 2)] == [2, 1]