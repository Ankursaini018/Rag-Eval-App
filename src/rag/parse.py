"""Turn documents into pages: one record per page, shaped {"doc": ..., "page": ..., "text": ...}."""
import re
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