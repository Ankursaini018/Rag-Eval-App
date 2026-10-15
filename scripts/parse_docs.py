"""Parse everything in docs/ into data/pages.jsonl.   Run:  python scripts/parse_docs.py"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.parse import parse_folder, write_jsonl  # noqa: E402

if __name__ == "__main__":
    pages = parse_folder(ROOT / "docs")
    write_jsonl(pages, ROOT / "data" / "pages.jsonl")
    per_doc = Counter(p["doc"] for p in pages)
    print(f"{len(pages)} pages from {len(per_doc)} documents -> data/pages.jsonl")
    for doc, n in per_doc.most_common(5):
        print(f"  {doc}: {n} pages")