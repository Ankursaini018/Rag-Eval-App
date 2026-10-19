from rag import generate
from rag.llm import LLMResult
from rag.search import Hit

HITS = [Hit("a::p1::c0", "a.pdf", 1, "Refunds take ten days.", 0.9),
        Hit("b::p4::c1", "b.md", 4, "Shipping is free.", 0.8)]


def fake_llm(reply, seen=None):
    def _complete(system, user):
        if seen is not None:
            seen.update(system=system, user=user)
        return LLMResult(reply, 50, 7)
    return _complete


def test_answer_uses_prompt_and_returns_text_and_tokens(monkeypatch):
    seen = {}
    monkeypatch.setattr(generate, "complete", fake_llm("  Ten days [1].  ", seen))
    out = generate.answer_question("How long do refunds take?", HITS)
    assert out["answer"] == "Ten days [1]." and out["input_tokens"] == 50 and out["output_tokens"] == 7
    assert "Refunds take ten days." in seen["user"] and "How long do refunds take?" in seen["user"]