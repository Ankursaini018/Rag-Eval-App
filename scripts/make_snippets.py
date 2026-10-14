"""Sample 100 sentences from YOUR documents in docs/ to practise embeddings on.
Run:  python scripts/make_snippets.py     ->  data/snippets.txt  (one snippet per line)"""
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS, OUT = ROOT / "docs", ROOT / "data" / "snippets.txt"


def clean(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)         # drop fenced code blocks
    text = re.sub(r"`[^`]*`", " ", text)                        # drop inline code
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)        # [label](url) -> label
    text = re.sub(r"<[^>]+>|^#+\s*|[*_>|]|\{[^}]*\}", " ", text, flags=re.M)
    return re.sub(r"\s+", " ", text)


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", clean(text))
    return [s.strip() for s in parts if 40 <= len(s.strip()) <= 300 and s.strip()[0].isupper()]


if __name__ == "__main__":
    found: list[str] = []
    for p in sorted(DOCS.rglob("*")):
        if p.suffix.lower() in {".md", ".txt", ".html", ".htm"}:
            found += sentences(p.read_text(errors="ignore"))
    found = list(dict.fromkeys(found))  # remove duplicates, keep order
    if len(found) < 100:
        sys.exit(f"Only {len(found)} usable sentences found in docs/. Add text/markdown docs.")
    random.Random(0).shuffle(found)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(found[:100]) + "\n")
    print(f"Wrote 100 snippets to {OUT}")