"""Turn documents into pages: one record per page, shaped {"doc": ..., "page": ..., "text": ...}."""
import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader


def parse_pdf(path: str | Path) -> list[dict]:
    """One record per PDF page. Page numbers start at 1 so they match what a human sees."""
    path = Path(path)
    reader = PdfReader(str(path))
    return [
        {"doc": path.name, "page": number, "text": page.extract_text() or ""}
        for number, page in enumerate(reader.pages, start=1)
    ]

def parse_html(path: str | Path) -> list[dict]:
    """A web page has no pages, so the whole page is page 1. Menus, scripts and footers are removed."""
    path = Path(path)
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside"]):
        tag.decompose()
    return [{"doc": path.name, "page": 1, "text": soup.get_text("\n")}]


def parse_text(path: str | Path, max_chars: int = 3000) -> list[dict]:
    """Markdown / plain text. These files have no pages either, but citations need a pointer and
    page-level evaluation needs more than one 'page' per file. So we cut the file into sections of
    about max_chars characters at blank lines. 'page' = section number."""
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    sections, current = [], ""
    for paragraph in re.split(r"\n\s*\n", text):
        if current and len(current) + len(paragraph) > max_chars:
            sections.append(current)
            current = ""
        current += paragraph + "\n\n"
    if current.strip():
        sections.append(current)
    return [{"doc": path.name, "page": i, "text": s} for i, s in enumerate(sections, start=1)]

def clean_text(text: str) -> str:
    """Fix the usual extraction damage without touching the meaning."""
    text = text.replace("\u00ad", "")                          # invisible soft hyphens
    text = text.replace("\r\n", "\n")
    text = re.sub(r"([a-z])-\n([a-z])", r"\1\2", text)         # 'inter-\nnational' -> 'international'
    text = re.sub(r"(?<=\S)[ \t]{2,}", " ", text)              # runs of spaces inside a line -> one space
    text = re.sub(r"[ \t]+$", "", text, flags=re.M)            # trailing spaces
    text = re.sub(r"\n{3,}", "\n\n", text)                     # many blank lines -> one
    return text.strip()


def strip_repeated_lines(pages: list[str], min_pages: int = 4, share: float = 0.5) -> list[str]:
    """Remove running headers and footers: short lines that appear on more than half of the pages.
    A page number at the start or end of a line is ignored when comparing, so 'Page 3' and 'Page 4'
    count as the same line. Digits in the middle of a line are NOT ignored (so numbered body lines survive)."""
    if len(pages) < min_pages:
        return pages

    def key(line: str) -> str:
        """Compare lines ignoring a page number at the start or end ('Page 3', '3 of 40', 'Title | 7')."""
        line = line.strip()
        line = re.sub(r"^(page\s+)?\d+(\s+of\s+\d+)?\s*[-|:]?\s*", "", line, flags=re.I)
        return re.sub(r"\s*[-|:]?\s*(page\s+)?\d+(\s+of\s+\d+)?$", "", line, flags=re.I)

    counts: Counter = Counter()
    for text in pages:
        lines = {key(ln) for ln in text.splitlines() if 0 < len(ln.strip()) < 80}
        counts.update(lines)
    repeated = {line for line, n in counts.items() if n / len(pages) > share}
    return ["\n".join(ln for ln in text.splitlines() if key(ln) not in repeated) for text in pages]


def normalize_pages(pages: list[dict], strip_headers: bool = False) -> list[dict]:
    """Clean the text of all pages of ONE document."""
    texts = [p["text"] for p in pages]
    if strip_headers:
        texts = strip_repeated_lines(texts)
    return [{**p, "text": clean_text(t)} for p, t in zip(pages, texts)]