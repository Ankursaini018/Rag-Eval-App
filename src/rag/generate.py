"""Turn retrieved chunks + a question into an answer."""
from .llm import complete
from .prompts import REFUSAL, SYSTEM_PROMPT, build_user_message


def is_refusal(answer: str) -> bool:
    """Did the model decline to answer? Tolerates curly apostrophes and extra words."""
    text = answer.strip().lower().replace("\u2019", "'")
    return text.startswith("i don't know") or "don't know based on the provided documents" in text


def answer_question(question: str, hits: list) -> dict:
    """Ask the LLM to answer from the given chunks only."""
    if not hits:   # nothing was retrieved: refusing is the only honest answer, and it costs no LLM call
        return {"answer": REFUSAL, "refused": True, "input_tokens": 0, "output_tokens": 0}
    result = complete(SYSTEM_PROMPT, build_user_message(question, hits))
    answer = result.text.strip()
    return {
        "answer": answer,
        "refused": is_refusal(answer),
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
    }