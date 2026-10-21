"""Embed all chunks and load them into Qdrant.
Run:  python scripts/build_index.py --size 500          (needs Qdrant running: docker compose up -d)
Rebuilding is safe: the collection is deleted and recreated each time."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.config import CHUNK_SIZE  # noqa: E402
from rag.embed import embed_chunks  # noqa: E402
from rag.parse import read_jsonl  # noqa: E402
from rag.store import get_client, index_chunks  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=CHUNK_SIZE, help="which chunks_<size>.jsonl to load")
    ap.add_argument("--collection", default=None, help="default: chunks_<size>")
    args = ap.parse_args()

    name = args.collection or f"chunks_{args.size}"
    chunks = read_jsonl(ROOT / "data" / f"chunks_{args.size}.jsonl")
    print(f"embedding {len(chunks)} chunks ...")
    vectors = embed_chunks(chunks)
    count = index_chunks(get_client(), name, chunks, vectors)
    print(f"collection '{name}' now holds {count} points")
    if count != len(chunks):
        sys.exit("ERROR: point count does not match chunk count")