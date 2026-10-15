from rag.parse import parse_html, parse_text


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