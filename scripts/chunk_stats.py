"""Print chunk statistics.   Run:  python scripts/chunk_stats.py [size]     (default 500)"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.chunk import chunk_stats  # noqa: E402
from rag.config import CHUNK_SIZE  # noqa: E402
from rag.parse import read_jsonl  # noqa: E402

if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else CHUNK_SIZE
    stats = chunk_stats(read_jsonl(ROOT / "data" / f"chunks_{size}.jsonl"), size)
    per_doc = stats.pop("chunks_per_doc")
    for key, value in stats.items():
        print(f"{key:>22}: {value}")
    ranked = sorted(per_doc.items(), key=lambda kv: kv[1])
    print("\nfewest chunks:", ranked[:3])
    print("most chunks:  ", ranked[-3:])