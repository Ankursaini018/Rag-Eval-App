"""Cut data/pages.jsonl into chunks.   Run:  python scripts/make_chunks.py --size 500 --overlap 50
Writes data/chunks_<size>.jsonl (the size is in the name so Day 15 can keep several versions)."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.chunk import chunk_pages  # noqa: E402
from rag.config import CHUNK_OVERLAP, CHUNK_SIZE  # noqa: E402
from rag.parse import read_jsonl, write_jsonl  # noqa: E402
from rag.tokens import get_tokenizer  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=CHUNK_SIZE, help="tokens per chunk")
    ap.add_argument("--overlap", type=int, default=CHUNK_OVERLAP, help="tokens shared between neighbouring chunks")
    args = ap.parse_args()

    pages = read_jsonl(ROOT / "data" / "pages.jsonl")
    chunks = chunk_pages(pages, args.size, args.overlap)
    out = ROOT / "data" / f"chunks_{args.size}.jsonl"
    write_jsonl(chunks, out)
    print(f"tokenizer: {get_tokenizer().name}")
    print(f"{len(pages)} pages -> {len(chunks)} chunks -> {out.relative_to(ROOT)}")