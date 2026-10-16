import pytest

from rag.chunk import chunk_page, chunk_pages, chunk_stats, make_chunk_id
from rag.tokens import WordTokenizer

TOK = WordTokenizer()


def page(n_words, doc="d.pdf", number=2):
    return {"doc": doc, "page": number, "text": " ".join(f"w{i}" for i in range(n_words))}


def test_no_chunk_exceeds_size():
    chunks = chunk_page(page(1000), size=100, overlap=10, tokenizer=TOK)
    assert len(chunks) > 1
    assert all(c["n_tokens"] <= 100 for c in chunks)
    assert all(len(c["text"].split()) == c["n_tokens"] for c in chunks)


def test_neighbouring_chunks_overlap_by_exactly_overlap_tokens():
    chunks = chunk_page(page(300), size=100, overlap=20, tokenizer=TOK)
    first, second = chunks[0]["text"].split(), chunks[1]["text"].split()
    assert first[-20:] == second[:20]


def test_every_word_lands_in_some_chunk():
    p = page(257)
    covered = {w for c in chunk_page(p, 100, 10, TOK) for w in c["text"].split()}
    assert covered == set(p["text"].split())


def test_last_chunk_is_not_a_pure_repeat():
    chunks = chunk_page(page(200), size=100, overlap=10, tokenizer=TOK)
    assert chunks[-1]["text"].split()[-1] == "w199"
    assert len(chunks) == 3          # windows start at 0, 90, 180


def test_exact_fit_gives_one_chunk():
    assert len(chunk_page(page(100), 100, 10, TOK)) == 1


def test_short_and_empty_pages():
    assert len(chunk_page(page(30), 100, 10, TOK)) == 1
    assert chunk_page({"doc": "d", "page": 1, "text": "   \n "}, 100, 10, TOK) == []


def test_original_text_is_preserved():
    text = "Hello World.\n\nSecond Paragraph, Here!"
    chunks = chunk_page({"doc": "d", "page": 1, "text": text}, 100, 10, TOK)
    assert chunks[0]["text"] == text          # capitals, newlines, punctuation untouched


@pytest.mark.parametrize("size,overlap", [(10, 10), (10, 11), (0, 0), (10, -1)])
def test_bad_settings_rejected(size, overlap):
    with pytest.raises(ValueError):
        chunk_page(page(10), size, overlap, TOK)


def test_ids_are_stable_unique_and_readable():
    a = chunk_pages([page(300), page(300, number=3)], 100, 10, TOK)
    b = chunk_pages([page(300), page(300, number=3)], 100, 10, TOK)
    assert [c["chunk_id"] for c in a] == [c["chunk_id"] for c in b]          # same input, same ids
    assert len({c["chunk_id"] for c in a}) == len(a)                          # no duplicates
    assert a[0]["chunk_id"] == "d.pdf::p2::c0" == make_chunk_id("d.pdf", 2, 0)


def test_stats():
    s = chunk_stats(chunk_pages([page(250)], 100, 10, TOK), size=100)
    assert s["chunks"] == 3 and s["docs"] == 1 and s["over_limit"] == 0 and s["max_tokens"] == 100