"""Ask every question in notes/day6_questions.txt (one per line) and write the results to
notes/day6_answers.md. No server needed.   Run:  python scripts/ask_questions.py"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.config import ASK_TOP_K as TOP_K  # noqa: E402
from rag.generate import answer_question  # noqa: E402
from rag.search import search  # noqa: E402



def run(questions: list[str], search_fn=search, answer_fn=answer_question) -> str:
    out = [f"# Day 6: 10 questions through the baseline pipeline\n\nRun on {date.today()} "
           f"(top {TOP_K} chunks, prompt v1, no tuning).\n"]
    for i, question in enumerate(questions, start=1):
        hits = search_fn(question, TOP_K)
        res = answer_fn(question, hits)
        cited = ", ".join(f"{c['doc']} p{c['page']}" for c in res["citations"]) or "none"
        retrieved = "; ".join(f"{h.doc} p{h.page} ({h.score:.2f})" for h in hits) or "nothing"
        out.append(
            f"## {i}. {question}\n\n"
            f"**Answer:** {res['answer']}\n\n"
            f"- Refused: {'yes' if res['refused'] else 'no'}\n"
            f"- Cited: {cited}\n"
            f"- Retrieved (doc page, score): {retrieved}\n"
            f"- **Verdict (fill in on Day 7):** [ ] correct  [ ] weak  [ ] wrong\n"
            f"- Why (your guess):\n"
        )
    return "\n".join(out)


TEMPLATE = """# One question per line. Lines starting with # are ignored.
# Write 10 real questions about YOUR documents, and delete the REPLACE words.
# Suggested mix: 4 direct fact questions, 2 worded differently from the document,
# 2 that need two passages, 2 that your documents do NOT answer.
REPLACE direct fact question 1
REPLACE direct fact question 2
REPLACE direct fact question 3
REPLACE direct fact question 4
REPLACE question worded differently from the document 1
REPLACE question worded differently from the document 2
REPLACE question that needs two passages 1
REPLACE question that needs two passages 2
REPLACE question the documents do NOT answer 1
REPLACE question the documents do NOT answer 2
"""

if __name__ == "__main__":
    src = ROOT / "notes" / "day6_questions.txt"
    if not src.exists():
        src.parent.mkdir(exist_ok=True)
        src.write_text(TEMPLATE, encoding="utf-8")
        sys.exit(f"I created {src.relative_to(ROOT)}. Replace the REPLACE lines with your 10 real questions, "
                 "then run this script again.")
    questions = [q.strip() for q in src.read_text(encoding="utf-8").splitlines()
                 if q.strip() and not q.startswith("#")]
    if not questions:
        sys.exit(f"Put your questions in {src.relative_to(ROOT)}, one per line.")
    if any(q.startswith("REPLACE") for q in questions):
        sys.exit("Some lines still start with REPLACE. Write your own question on each of those lines first.")
    (ROOT / "notes" / "day6_answers.md").write_text(run(questions), encoding="utf-8")
    print(f"Wrote notes/day6_answers.md with {len(questions)} questions. Read it, then do Day 7.")