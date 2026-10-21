"""Cut pages into overlapping chunks of a fixed number of tokens."""
from .config import CHUNK_OVERLAP, CHUNK_SIZE
from .tokens import get_tokenizer

def make_chunk_id(doc: str, page: int, index: int) -> str:
    """Readable and stable: the same input always gives the same ID. 'handbook.pdf::p3::c1'"""
    return f"{doc}::p{page}::c{index}"

def chunk_page(page: dict, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP, tokenizer=None) -> list[dict]:
    """Slide a window of `size` tokens over the page, moving forward by size - overlap each time.
    Chunks never cross a page boundary, so every chunk belongs to exactly one (doc, page)."""
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("need size > 0 and 0 <= overlap < size")
    tokenizer = tokenizer or get_tokenizer()
    text = page["text"]
    spans = tokenizer.spans(text)
    chunks = []
    start = 0
    while start < len(spans):
        window = spans[start:start + size]
        chunks.append({
            "chunk_id": make_chunk_id(page["doc"], page["page"], len(chunks)),
            "doc": page["doc"],
            "page": page["page"],
            "index": len(chunks),                                  # 0, 1, 2 ... within this page
            "text": text[window[0][0]:window[-1][1]].strip(),      # cut from the ORIGINAL text
            "n_tokens": len(window),
        })
        if start + size >= len(spans):                             # this window reached the end
            break
        start += size - overlap
    return chunks

def chunk_pages(pages: list[dict], size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP, tokenizer=None) -> list[dict]:
    """Chunk every page of every document."""
    tokenizer = tokenizer or get_tokenizer()
    chunks = []
    for page in pages:
        chunks.extend(chunk_page(page, size, overlap, tokenizer))
    return chunks

def chunk_stats(chunks: list[dict], size: int = CHUNK_SIZE) -> dict:
    """Numbers that tell you whether chunking behaved."""
    if not chunks:
        return {"chunks": 0}
    sizes = sorted(c["n_tokens"] for c in chunks)
    per_doc: dict[str, int] = {}
    for c in chunks:
        per_doc[c["doc"]] = per_doc.get(c["doc"], 0) + 1
    return {
        "chunks": len(chunks),
        "docs": len(per_doc),
        "avg_tokens": round(sum(sizes) / len(sizes), 1),
        "min_tokens": sizes[0],
        "median_tokens": sizes[len(sizes) // 2],
        "max_tokens": sizes[-1],
        "tiny_chunks_under_50": sum(1 for s in sizes if s < 50),
        "over_limit": sum(1 for s in sizes if s > size),
        "chunks_per_doc": per_doc,
    }