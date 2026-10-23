from rag.golden_checks import (composition, composition_markdown, find_copied_questions,
                               find_near_duplicates, longest_common_run, words)


def entry(qid, question, type="single_fact", gold=({"doc": "a.html", "page": 1},)):
    return {"id": qid, "question": question, "type": type, "answer": "x", "gold": list(gold)}


def test_longest_common_run():
    a = words("How do I declare a path parameter in the route")
    b = words("You declare a path parameter by using curly braces")
    assert longest_common_run(a, b) == 4          # "declare a path parameter"
    assert longest_common_run(a, words("nothing shared here")) == 0
    assert longest_common_run([], b) == 0


def test_near_duplicates_found_but_different_questions_are_not():
    entries = [entry("q001", "How do I declare a path parameter?"),
               entry("q002", "how do i declare a path parameter"),
               entry("q003", "What status code does a created item return?")]
    pairs = find_near_duplicates(entries)
    assert [(a, b) for a, b, _ in pairs] == [("q001", "q002")]


def test_copied_question_is_flagged_and_reworded_one_is_not():
    pages = [{"doc": "a.html", "page": 1,
              "text": "Path parameters are declared with the same syntax used by Python format strings."}]
    copied = entry("q001", "Are path parameters declared with the same syntax used by Python format strings?")
    reworded = entry("q002", "What notation marks a variable part of a URL?")
    flagged = find_copied_questions([copied, reworded], pages, max_run=6)
    assert [q for q, _ in flagged] == ["q001"]


def test_unanswerable_entries_have_no_pages_to_copy_from():
    e = entry("q001", "What is the capital of France?", type="unanswerable", gold=())
    assert find_copied_questions([e], [{"doc": "a.html", "page": 1, "text": "x"}]) == []


def test_composition_counts_and_markdown():
    entries = [entry("q001", "aaa aaa aaa aaa"), entry("q002", "bbb bbb bbb bbb", type="tricky"),
               entry("q003", "ccc ccc ccc ccc", type="unanswerable", gold=())]
    c = composition(entries)
    assert c["total"] == 3 and c["by_type"]["tricky"] == 1 and c["by_doc"]["a.html"] == 2
    md = composition_markdown(entries)
    assert "| single_fact | 1 | 33% |" in md and "| a.html | 2 |" in md