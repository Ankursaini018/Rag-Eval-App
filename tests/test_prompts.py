from rag.prompts import SYSTEM_PROMPT, build_context, build_user_message
from rag.search import Hit

HITS = [Hit("a::p1::c0", "a.pdf", 1, "Refunds take ten days.", 0.9),
        Hit("b::p4::c1", "b.md", 4, "Shipping is free.", 0.8)]


def test_context_numbers_and_labels_passages():
    ctx = build_context(HITS)
    assert ctx.startswith("[1] (source: a.pdf, page 1)\nRefunds take ten days.")
    assert "[2] (source: b.md, page 4)\nShipping is free." in ctx


def test_user_message_contains_context_and_question():
    msg = build_user_message("How long do refunds take?", HITS)
    assert "Refunds take ten days." in msg and msg.endswith("Question: How long do refunds take?")


def test_prompt_demands_context_only_and_citations():
    assert "ONLY" in SYSTEM_PROMPT and "square brackets" in SYSTEM_PROMPT