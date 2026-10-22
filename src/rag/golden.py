"""The golden set: hand-written questions with known answers and known source pages.
One JSON object per line in data/golden.jsonl. This module only loads and checks it."""
import json
import re
from pathlib import Path

# single_fact    : one fact, stated in one place
# multi_chunk    : the answer needs 2+ separate pages
# unanswerable   : the documents do NOT contain the answer (the correct reply is a refusal)
# paraphrase     : answerable, but worded differently from the document (Day 9)
# tricky         : answerable, but the wording is misleading or has a trap (Day 9)
TYPES = ("single_fact", "multi_chunk", "unanswerable", "paraphrase", "tricky")
REQUIRED = ("id", "question", "type", "answer", "gold")
ALLOWED = REQUIRED + ("notes",)
ID_PATTERN = re.compile(r"^q\d{3}$")


def load_golden(path: str | Path) -> list[dict]:
    entries = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"line {number}: not valid JSON ({e.msg})") from e
    return entries


def _normalize(question: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", question.lower()).strip()


def validate_entries(entries: list[dict], pages: list[dict] | None = None) -> list[str]:
    """Return a list of problems (empty list = all good).
    If `pages` (the rows of data/pages.jsonl) is given, also check every cited page really exists."""
    problems: list[str] = []
    known = {(p["doc"], p["page"]) for p in pages} if pages is not None else None
    seen_ids: set[str] = set()
    seen_questions: dict[str, str] = {}

    for i, e in enumerate(entries, start=1):
        name = e.get("id") if isinstance(e, dict) and e.get("id") else f"entry #{i}"

        def bad(msg: str) -> None:
            problems.append(f"{name}: {msg}")

        if not isinstance(e, dict):
            bad("is not a JSON object")
            continue
        for key in REQUIRED:
            if key not in e:
                bad(f"missing field '{key}'")
        for key in e:
            if key not in ALLOWED:
                bad(f"unknown field '{key}'")
        if any(key not in e for key in REQUIRED):
            continue

        if not isinstance(e["id"], str) or not ID_PATTERN.match(e["id"]):
            bad("id must look like q001")
        elif e["id"] in seen_ids:
            bad("duplicate id")
        seen_ids.add(str(e["id"]))

        q = e["question"]
        if not isinstance(q, str) or not 10 <= len(q.strip()) <= 300:
            bad("question must be text of 10-300 characters")
        else:
            norm = _normalize(q)
            if norm in seen_questions:
                bad(f"same question as {seen_questions[norm]}")
            seen_questions[norm] = str(e["id"])

        if e["type"] not in TYPES:
            bad(f"type must be one of {', '.join(TYPES)}")
            continue

        gold = e["gold"]
        if not isinstance(gold, list):
            bad("gold must be a list")
            continue

        if e["type"] == "unanswerable":
            if e["answer"] is not None:
                bad("unanswerable questions must have answer null")
            if gold:
                bad("unanswerable questions must have gold []")
            continue

        if not isinstance(e["answer"], str) or not e["answer"].strip():
            bad("answer must be non-empty text")
        if not gold:
            bad("gold must list at least one {doc, page}")
        distinct = set()
        for g in gold:
            if not (isinstance(g, dict) and set(g) == {"doc", "page"}
                    and isinstance(g["doc"], str) and isinstance(g["page"], int) and g["page"] >= 1):
                bad(f"bad gold entry {g!r}; expected {{\"doc\": \"file.pdf\", \"page\": 3}}")
                continue
            distinct.add((g["doc"], g["page"]))
            if known is not None and (g["doc"], g["page"]) not in known:
                bad(f"cited page does not exist: {g['doc']} page {g['page']}")
        if len(distinct) != len(gold):
            bad("gold lists the same page twice")
        if e["type"] == "multi_chunk" and len(distinct) < 2:
            bad("multi_chunk needs 2 or more different pages in gold")
    return problems