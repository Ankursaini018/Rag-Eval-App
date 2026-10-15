"""Turn documents into pages: one record per page, shaped {"doc": ..., "page": ..., "text": ...}."""
from pathlib import Path

from pypdf import PdfReader


def parse_pdf(path: str | Path) -> list[dict]:
    """One record per PDF page. Page numbers start at 1 so they match what a human sees."""
    path = Path(path)
    reader = PdfReader(str(path))
    return [
        {"doc": path.name, "page": number, "text": page.extract_text() or ""}
        for number, page in enumerate(reader.pages, start=1)
    ]