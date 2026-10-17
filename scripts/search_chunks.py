"""Try the real search from the terminal.   Run:  python scripts/search_chunks.py "your question" [k]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag.search import search  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: python scripts/search_chunks.py "your question" [k]')
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    for rank, hit in enumerate(search(sys.argv[1], k), start=1):
        preview = hit.text[:160].replace("\n", " ")
        print(f"{rank}. {hit.score:.3f}  {hit.doc} p{hit.page}  [{hit.chunk_id}]\n   {preview}...\n")