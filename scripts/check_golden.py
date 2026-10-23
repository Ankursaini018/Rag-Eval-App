"""Look for questions that are duplicates of each other or copied from the documents.
Run:  python scripts/check_golden.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.golden import load_golden  # noqa: E402
from rag.golden_checks import find_copied_questions, find_near_duplicates  # noqa: E402
from rag.parse import read_jsonl  # noqa: E402

if __name__ == "__main__":
    entries = load_golden(ROOT / "data" / "golden.jsonl")
    pages = read_jsonl(ROOT / "data" / "pages.jsonl")
    dupes = find_near_duplicates(entries)
    copied = find_copied_questions(entries, pages)

    print(f"checked {len(entries)} questions")
    for a, b, ratio in dupes:
        print(f"  NEAR-DUPLICATE: {a} and {b} (similarity {ratio})")
    for qid, run in copied:
        print(f"  COPIED: {qid} repeats {run} words in a row from its source page; reword it")
    if dupes or copied:
        sys.exit(1)
    print("OK: no duplicates, nothing copied from the text")