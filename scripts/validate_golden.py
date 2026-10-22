"""Check data/golden.jsonl. Run after every few questions you add.
Run:  python scripts/validate_golden.py              (format checks)
      python scripts/validate_golden.py --pages      (also checks cited pages exist in data/pages.jsonl)"""
import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.golden import TYPES, load_golden, validate_entries  # noqa: E402
from rag.parse import read_jsonl  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(ROOT / "data" / "golden.jsonl"))
    ap.add_argument("--pages", action="store_true", help="also check cited pages exist")
    args = ap.parse_args()

    try:
        entries = load_golden(args.file)
    except (OSError, ValueError) as e:
        sys.exit(f"ERROR: {e}")
    pages = read_jsonl(ROOT / "data" / "pages.jsonl") if args.pages else None
    problems = validate_entries(entries, pages)

    counts = Counter(e.get("type") for e in entries if isinstance(e, dict))
    print(f"{len(entries)} questions: " + ", ".join(f"{t}={counts.get(t, 0)}" for t in TYPES))
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("OK: no problems found")