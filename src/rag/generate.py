"""Turn retrieved chunks + a question into an answer."""
from .llm import complete
from .prompts import SYSTEM_PROMPT, build_user_message


def answer_question(question: str, hits: list) -> dict:
    """Ask the LLM to answer from the given chunks only."""
    result = complete(SYSTEM_PROMPT, build_user_message(question, hits))
    return {
        "answer": result.text.strip(),
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
    }