"""Tests on the REAL data/golden.jsonl. They are skipped when the data files are not present."""
from pathlib import Path

import pytest

from rag.golden import load_golden, validate_entries
from rag.parse import read_jsonl

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "data" / "golden.jsonl"
PAGES = ROOT / "data" / "pages.jsonl"

pytestmark = pytest.mark.skipif(not (GOLDEN.exists() and PAGES.exists()),
                                reason="data/golden.jsonl or data/pages.jsonl not present")


def test_golden_has_exactly_50_entries():
    assert len(load_golden(GOLDEN)) == 50


def test_every_entry_is_valid_and_every_cited_page_exists():
    problems = validate_entries(load_golden(GOLDEN), read_jsonl(PAGES))
    assert problems == [], "\n".join(problems)


def test_unanswerable_share_is_at_least_ten_percent():
    entries = load_golden(GOLDEN)
    share = sum(e["type"] == "unanswerable" for e in entries) / len(entries)
    assert share >= 0.10