"""Look at the source text while writing golden questions.
Run:  python scripts/show_page.py --list                  (every doc and its page count)
      python scripts/show_page.py tutorial.html 3         (print one page)
      python scripts/show_page.py --find "path parameter" (which pages contain this phrase)"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.parse import read_jsonl  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("doc", nargs="?")
    ap.add_argument("page", nargs="?", type=int)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--find")
    args = ap.parse_args()
    pages = read_jsonl(ROOT / "data" / "pages.jsonl")

    if args.list:
        counts: dict[str, int] = {}
        for p in pages:
            counts[p["doc"]] = counts.get(p["doc"], 0) + 1
        for doc, n in sorted(counts.items()):
            print(f"{n:4d} pages  {doc}")
    elif args.find:
        needle = args.find.lower()
        for p in pages:
            if needle in p["text"].lower():
                print(f"{p['doc']}  page {p['page']}")
    elif args.doc and args.page:
        for p in pages:
            if p["doc"] == args.doc and p["page"] == args.page:
                print(p["text"])
                break
        else:
            sys.exit("no such page; use --list to see names")
    else:
        ap.print_help()