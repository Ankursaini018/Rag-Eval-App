"""The words we send to the LLM. Kept in one file so prompt changes are easy to find, review and compare."""

SYSTEM_PROMPT = """You answer questions using ONLY the numbered context passages provided by the user.
Rules:
1. Use only information that is in the passages. Do not use outside knowledge, even if you are sure of the answer.
2. After every claim, cite the passage it came from with its number in square brackets, like [1] or [2][3].
3. Be concise and direct."""


def build_context(hits: list) -> str:
    """Number the passages [1], [2], ... and label each with its source, so the model can cite them."""
    return "\n\n".join(
        f"[{i}] (source: {h.doc}, page {h.page})\n{h.text}" for i, h in enumerate(hits, start=1)
    )


def build_user_message(question: str, hits: list) -> str:
    return f"Context passages:\n\n{build_context(hits)}\n\nQuestion: {question}"