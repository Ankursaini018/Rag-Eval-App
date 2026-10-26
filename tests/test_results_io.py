import csv
import json

from rag.results_io import first_gold_rank, save_result, write_csv

RESULT = {
    "retriever": "fake", "ks": [1, 3, 5], "depth": 10,
    "rows": [
        {"id": "q001", "type": "single_fact", "question": "Q, with comma?", "gold": [["a", 1]],
         "retrieved": [["x", 1], ["a", 1]], "recall@1": 0.0, "recall@3": 1.0, "recall@5": 1.0, "rr": 0.5},
        {"id": "q002", "type": "tricky", "question": "Missed?", "gold": [["a", 2]],
         "retrieved": [["x", 1]], "recall@1": 0.0, "recall@3": 0.0, "recall@5": 0.0, "rr": 0.0},
    ],
}


def test_first_gold_rank():
    assert first_gold_rank([["x", 1], ["a", 1]], [["a", 1]]) == 2
    assert first_gold_rank([["x", 1]], [["a", 1]]) is None


def test_save_result_roundtrip(tmp_path):
    path = save_result(RESULT, tmp_path / "sub" / "r.json")
    assert json.loads(path.read_text(encoding="utf-8")) == RESULT


def test_csv_has_one_row_per_question_and_quotes_commas(tmp_path):
    path = write_csv(RESULT, tmp_path / "r.csv")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 2
    assert rows[0]["question"] == "Q, with comma?" and rows[0]["first_gold_rank"] == "2"
    assert rows[1]["first_gold_rank"] == "" and rows[1]["recall@5"] == "0.0"