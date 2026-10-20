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


def test_refusal_is_detected(monkeypatch):
    monkeypatch.setattr(generate, "complete", fake_llm("I don\u2019t know based on the provided documents."))
    assert generate.answer_question("Who founded it?", HITS)["refused"] is True


def test_normal_answer_is_not_a_refusal(monkeypatch):
    monkeypatch.setattr(generate, "complete", fake_llm("Ten days [1]."))
    assert generate.answer_question("q", HITS)["refused"] is False


def test_no_hits_refuses_without_calling_the_llm(monkeypatch):
    def boom(*a):
        raise AssertionError("the LLM must not be called when nothing was retrieved")
    monkeypatch.setattr(generate, "complete", boom)
    out = generate.answer_question("q", [])
    assert out["refused"] is True and out["answer"] == "I don't know based on the provided documents."


def test_prompt_contains_the_exact_refusal_sentence():
    from rag.prompts import REFUSAL, SYSTEM_PROMPT
    assert REFUSAL in SYSTEM_PROMPT