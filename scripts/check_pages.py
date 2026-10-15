"""Flag empty or garbled pages in data/pages.jsonl.   Run:  python scripts/check_pages.py"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.parse import read_jsonl  # noqa: E402


def problems(text: str) -> list[str]:
    found = []
    if len(text.strip()) < 50:
        found.append("almost empty (a scanned image? needs OCR)")
    elif sum(c.isalpha() for c in text) / len(text) < 0.5:
        found.append("less than half letters (table, formula or garbage?)")
    if re.search(r"(.)\1{9,}", text):
        found.append("a character repeated 10+ times in a row")
    if "\ufffd" in text:
        found.append("replacement characters (encoding problem)")
    if re.search(r"\b(\w)\s(\w)\s(\w)\s(\w)\s(\w)\s(\w)\b", text):
        found.append("letters separated by spaces (bad PDF font mapping?)")
    return found


if __name__ == "__main__":
    pages = read_jsonl(ROOT / "data" / "pages.jsonl")
    flagged = 0
    for p in pages:
        issues = problems(p["text"])
        if issues:
            flagged += 1
            print(f"{p['doc']} page {p['page']}: {'; '.join(issues)}")
    print(f"\nChecked {len(pages)} pages, flagged {flagged}.")
    sys.exit(1 if flagged else 0)