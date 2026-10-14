"""Type a question, see the 3 snippets closest in meaning.
Run:  python scripts/search_snippets.py "how do I declare a path parameter"
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.embed import embed_cached, embed_query  # noqa: E402
from rag.similarity import top_k  # noqa: E402

SNIPPETS = ROOT / "data" / "snippets.txt"
CACHE = ROOT / "data" / "snippet_vectors.npz"


def search(query: str, k: int = 3) -> list[tuple[float, str]]:
    snippets = [s for s in SNIPPETS.read_text().splitlines() if s.strip()]
    vectors = embed_cached(snippets, CACHE)          # slow the first time, instant after
    return [(score, snippets[i]) for i, score in top_k(embed_query(query), vectors, k)]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: python scripts/search_snippets.py "your question"')
    for score, text in search(" ".join(sys.argv[1:])):
        print(f"{score:.3f}  {text}\n")