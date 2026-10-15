from reportlab.pdfgen import canvas

from rag.parse import parse_document, parse_pdf

BODIES = ["Refunds are issued within ten days.", "Shipping is free above fifty dollars.",
          "Support answers email within a day.", "The shop opens at nine every morning.",
          "Returns need the original receipt.", "Gift cards never expire."]


def make_pdf(path, n_pages=6):
    c = canvas.Canvas(str(path))
    for i in range(1, n_pages + 1):
        c.drawString(72, 800, "ACME Corp Handbook")                       # running header
        c.drawString(72, 700, BODIES[i - 1])
        c.drawString(72, 40, f"Page {i}")                                  # running footer
        c.showPage()
    c.save()


def test_pdf_page_numbers_and_text(tmp_path):
    f = tmp_path / "handbook.pdf"
    make_pdf(f)
    pages = parse_pdf(f)
    assert [p["page"] for p in pages] == [1, 2, 3, 4, 5, 6]
    assert pages[2]["doc"] == "handbook.pdf" and BODIES[2] in pages[2]["text"]


def test_pdf_headers_and_footers_removed(tmp_path):
    f = tmp_path / "handbook.pdf"
    make_pdf(f)
    pages = parse_document(f)
    assert all("ACME" not in p["text"] and "Page" not in p["text"] for p in pages)
    assert [p["text"] for p in pages] == BODIES