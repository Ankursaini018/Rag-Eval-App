from rag.parse import clean_text, normalize_pages, parse_html, parse_text, strip_repeated_lines, parse_document, read_jsonl, write_jsonl


def test_parse_text_sections_and_numbering(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("\n\n".join(f"Paragraph {i} " + "word " * 100 for i in range(20)))
    pages = parse_text(f, max_chars=1000)
    assert len(pages) > 1
    assert [p["page"] for p in pages] == list(range(1, len(pages) + 1))
    assert all(p["doc"] == "a.md" for p in pages)


def test_parse_html_drops_menus_and_scripts(tmp_path):
    f = tmp_path / "p.html"
    f.write_text("<html><nav>MENU</nav><script>var x=1;</script><body><h1>Title</h1><p>Real text.</p>"
                 "<footer>FOOT</footer></body></html>")
    text = parse_html(f)[0]["text"]
    assert "Real text." in text and "MENU" not in text and "var x" not in text and "FOOT" not in text


def test_clean_text():
    assert clean_text("inter-\nnational  law\u00ad") == "international law"
    assert clean_text("a\n\n\n\n\nb") == "a\n\nb"
    assert clean_text("x\n    keep indent") == "x\n    keep indent"
    assert clean_text("well-\nKnown") == "well-\nKnown"          # real hyphen before a capital is kept


def test_strip_repeated_lines():
    bodies = ["refunds take ten days", "shipping is free", "contact support", "opening hours", "returns policy", "gift cards"]
    pages = [f"ACME Corp Handbook\n{b}\nPage {i}" for i, b in enumerate(bodies, start=1)]
    assert strip_repeated_lines(pages) == bodies


def test_numbered_body_lines_survive():
    # 'Step N of the process' differs on every page (digit in the middle), so it is body text, not a header
    pages = [f"Step {i} of the process\nunique {w}" for i, w in enumerate("abcdef", start=1)]
    assert strip_repeated_lines(pages) == pages


def test_strip_needs_enough_pages():
    pages = ["Header\nA", "Header\nB"]
    assert strip_repeated_lines(pages) == pages


def test_normalize_keeps_other_fields():
    out = normalize_pages([{"doc": "d", "page": 3, "text": "a  b"}])
    assert out == [{"doc": "d", "page": 3, "text": "a b"}]


def test_jsonl_roundtrip(tmp_path):
    rows = [{"doc": "d", "page": 1, "text": "héllo"}]
    write_jsonl(rows, tmp_path / "x" / "p.jsonl")
    assert read_jsonl(tmp_path / "x" / "p.jsonl") == rows


def test_unknown_type_skipped(tmp_path):
    f = tmp_path / "x.bin"
    f.write_bytes(b"\x00")
    assert parse_document(f) == []