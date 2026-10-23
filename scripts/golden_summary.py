"""Print the golden-set composition table (markdown).
Run:  python scripts/golden_summary.py                 (print)
      python scripts/golden_summary.py --write         (write docs/golden_composition.md)"""
import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.golden import load_golden  # noqa: E402
from rag.golden_checks import composition_markdown  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    table = composition_markdown(load_golden(ROOT / "data" / "golden.jsonl"))
    if args.write:
        out = ROOT / "docs" / "golden_composition.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text(f"# Golden set composition\n\nGenerated {date.today()} by "
                       f"`scripts/golden_summary.py` from `data/golden.jsonl`.\n\n{table}\n", encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    else:
        print(table)