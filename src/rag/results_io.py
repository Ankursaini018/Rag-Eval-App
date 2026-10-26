"""Save and export evaluation results."""
import csv
import json
from pathlib import Path


def save_result(result: dict, path: str | Path) -> Path:
    """Write the full result (summary, per-type numbers, every question's row) as readable JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def first_gold_rank(retrieved: list, gold: list) -> int | None:
    """Position (1 = best) of the first retrieved page that is a gold page, or None if not retrieved."""
    gold_set = {tuple(g) for g in gold}
    for position, page in enumerate(retrieved, start=1):
        if tuple(page) in gold_set:
            return position
    return None


def write_csv(result: dict, path: str | Path) -> Path:
    """One row per scored question, easy to open in Excel and sort by 'first_gold_rank'."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ks = result["ks"]
    columns = ["id", "type", "question", "gold_pages", "first_gold_rank", *[f"recall@{k}" for k in ks],
               "rr", "retrieved_top5"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for r in result["rows"]:
            rank = first_gold_rank(r["retrieved"], r["gold"])
            writer.writerow([
                r["id"], r["type"], r["question"],
                "; ".join(f"{d} p{p}" for d, p in r["gold"]),
                rank if rank is not None else "",
                *[r[f"recall@{k}"] for k in ks],
                round(r["rr"], 4),
                "; ".join(f"{d} p{p}" for d, p in r["retrieved"][:5]),
            ])
    return path