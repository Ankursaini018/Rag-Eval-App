"""Cut pages into overlapping chunks of a fixed number of tokens."""
from .tokens import get_tokenizer


def chunk_page(page: dict, size: int = 500, overlap: int = 50, tokenizer=None) -> list[dict]:
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