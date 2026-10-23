"""Quality checks on the golden set: copy-pasted questions, near-duplicates, and a composition summary."""
import re
from collections import Counter
from difflib import SequenceMatcher

from .golden import TYPES


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def longest_common_run(a: list[str], b: list[str]) -> int:
    """Length (in words) of the longest stretch of words that appears in BOTH lists, in the same order."""
    best = 0
    previous = [0] * (len(b) + 1)
    for x in a:
        current = [0] * (len(b) + 1)
        for j, y in enumerate(b, start=1):
            if x == y:
                current[j] = previous[j - 1] + 1
                best = max(best, current[j])
        previous = current
    return best


def find_near_duplicates(entries: list[dict], threshold: float = 0.8) -> list[tuple[str, str, float]]:
    """Pairs of questions whose wording is almost the same (ratio 1.0 = identical)."""
    pairs = []
    texts = [(e["id"], " ".join(words(e["question"]))) for e in entries]
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            ratio = SequenceMatcher(None, texts[i][1], texts[j][1]).ratio()
            if ratio >= threshold:
                pairs.append((texts[i][0], texts[j][0], round(ratio, 2)))
    return pairs


def find_copied_questions(entries: list[dict], pages: list[dict], max_run: int = 6) -> list[tuple[str, int]]:
    """Questions that repeat `max_run` or more words in a row from one of their own gold pages.
    A question lifted from the text is too easy: search can match it word for word."""
    text_of = {(p["doc"], p["page"]): words(p["text"]) for p in pages}
    flagged = []
    for e in entries:
        q = words(e["question"])
        run = max((longest_common_run(q, text_of.get((g["doc"], g["page"]), [])) for g in e["gold"]), default=0)
        if run >= max_run:
            flagged.append((e["id"], run))
    return flagged


def composition(entries: list[dict]) -> dict:
    """Counts the numbers for the composition table."""
    by_type = Counter(e["type"] for e in entries)
    by_doc = Counter(g["doc"] for e in entries for g in e["gold"])
    return {"total": len(entries), "by_type": by_type, "by_doc": by_doc}


def composition_markdown(entries: list[dict]) -> str:
    c = composition(entries)
    total = c["total"] or 1
    lines = ["| Type | Questions | Share |", "|---|---:|---:|"]
    for t in TYPES:
        n = c["by_type"].get(t, 0)
        lines.append(f"| {t} | {n} | {100 * n / total:.0f}% |")
    lines.append(f"| **total** | **{c['total']}** | **100%** |")
    lines += ["", "| Document | Gold citations |", "|---|---:|"]
    for doc, n in sorted(c["by_doc"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {doc} | {n} |")
    return "\n".join(lines)