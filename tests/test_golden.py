import json

import pytest

from rag.golden import load_golden, validate_entries


def good(**over):
    e = {"id": "q001", "question": "How do you declare a path parameter?", "type": "single_fact",
         "answer": "Put the name in curly braces in the path.", "gold": [{"doc": "a.html", "page": 1}]}
    e.update(over)
    return e


def test_valid_entries_pass():
    entries = [good(),
               good(id="q002", question="Which two pages explain CORS and middleware?", type="multi_chunk",
                    gold=[{"doc": "a.html", "page": 1}, {"doc": "a.html", "page": 2}]),
               good(id="q003", question="What is the capital of France?", type="unanswerable",
                    answer=None, gold=[])]
    assert validate_entries(entries) == []


@pytest.mark.parametrize("entry, fragment", [
    (good(type="easy"), "type must be"),
    (good(id="7"), "id must look like"),
    (good(question="short"), "10-300"),
    (good(answer=""), "answer must be non-empty"),
    (good(gold=[]), "at least one"),
    (good(gold=[{"doc": "a.html", "page": 0}]), "bad gold entry"),
    (good(gold=[{"doc": "a.html", "page": 1}, {"doc": "a.html", "page": 1}]), "same page twice"),
    (good(type="multi_chunk"), "2 or more different pages"),
    (good(type="unanswerable"), "must have answer null"),
    (good(type="unanswerable", answer=None), "must have gold []"),
    (good(extra=1), "unknown field"),
])
def test_each_rule_catches_its_problem(entry, fragment):
    problems = validate_entries([entry])
    assert any(fragment in p for p in problems), problems


def test_missing_field_duplicate_id_and_duplicate_question():
    broken = good()
    del broken["gold"]
    assert any("missing field 'gold'" in p for p in validate_entries([broken]))
    dup = validate_entries([good(), good()])
    assert any("duplicate id" in p for p in dup) and any("same question" in p for p in dup)


def test_cited_pages_must_exist_when_pages_given():
    pages = [{"doc": "a.html", "page": 1, "text": "x"}]
    assert validate_entries([good()], pages) == []
    problems = validate_entries([good(gold=[{"doc": "a.html", "page": 9}])], pages)
    assert any("does not exist" in p for p in problems)


def test_load_golden_skips_blank_lines_and_reports_bad_json(tmp_path):
    f = tmp_path / "g.jsonl"
    f.write_text(json.dumps(good()) + "\n\n", encoding="utf-8")
    assert len(load_golden(f)) == 1
    f.write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 1"):
        load_golden(f)