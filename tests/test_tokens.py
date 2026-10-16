import pytest

from rag.embed import MODEL_NAME
from rag.tokens import HFTokenizer, WordTokenizer, count_tokens


def test_word_tokenizer_spans_point_into_the_text():
    text = "Hello  big world"
    spans = WordTokenizer().spans(text)
    assert [text[a:b] for a, b in spans] == ["Hello", "big", "world"]
    assert count_tokens(text, WordTokenizer()) == 3


class StubHF:
    """Mimics a Hugging Face fast tokenizer's output shape."""
    def __call__(self, text, add_special_tokens, return_offsets_mapping):
        return {"offset_mapping": [(0, 5), (5, 8)]}


def test_hf_wrapper_returns_integer_spans():
    assert HFTokenizer(StubHF(), "stub").spans("whatever") == [(0, 5), (5, 8)]


def test_real_model_tokenizer_keeps_chunks_inside_the_512_limit():
    """Runs only if the bge tokenizer is available locally (it is, after Day 2)."""
    try:
        tok = HFTokenizer.load(MODEL_NAME)
    except Exception:
        pytest.skip("bge tokenizer not available offline")
    from rag.chunk import chunk_page
    text = " ".join(f"Sentence number {i} talks about Refund Policies and shipping." for i in range(400))
    chunks = chunk_page({"doc": "d", "page": 1, "text": text}, 500, 50, tok)
    assert len(chunks) > 1
    for c in chunks:
        assert len(tok._tok(c["text"])["input_ids"]) <= 512     # includes the 2 special tokens
    assert chunks[0]["text"].startswith("Sentence number 0")       # capitals preserved