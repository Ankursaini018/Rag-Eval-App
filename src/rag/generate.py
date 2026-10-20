"""Turn retrieved chunks + a question into an answer."""
import re

from .llm import complete
from .prompts import REFUSAL, SYSTEM_PROMPT, build_user_message


def is_refusal(answer: str) -> bool:
    """Did the model decline to answer? Tolerates curly apostrophes and extra words."""
    text = answer.strip().lower().replace("\u2019", "'")
    return text.startswith("i don't know") or "don't know based on the provided documents" in text


def parse_citation_numbers(answer: str, n_passages: int) -> list[int]:
    """Find [1], [2][3], [1, 2] in the answer. Returns the passage numbers cited, in order of first use,
    ignoring numbers that do not exist (a model can invent '[7]' when it only saw 5 passages)."""
    found: list[int] = []
    for group in re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", answer):
        for number in re.split(r"\s*,\s*", group):
            n = int(number)
            if 1 <= n <= n_passages and n not in found:
                found.append(n)
    return found


def build_citations(answer: str, hits: list) -> list[dict]:
    """Map the cited numbers back to the real chunks: this is how the app 'shows where it came from'."""
    return [
        {"n": n, "chunk_id": hits[n - 1].chunk_id, "doc": hits[n - 1].doc, "page": hits[n - 1].page,
         "text": hits[n - 1].text}
        for n in parse_citation_numbers(answer, len(hits))
    ]


def answer_question(question: str, hits: list) -> dict:
    """Ask the LLM to answer from the given chunks only."""
    if not hits:   # nothing was retrieved: refusing is the only honest answer, and it costs no LLM call
        return {"answer": REFUSAL, "refused": True, "citations": [], "input_tokens": 0, "output_tokens": 0}
    result = complete(SYSTEM_PROMPT, build_user_message(question, hits))
    answer = result.text.strip()
    return {
        "answer": answer,
        "refused": is_refusal(answer),
        "citations": build_citations(answer, hits),
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
    }