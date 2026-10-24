"""Run a retriever over the golden set and compute recall@k and MRR. Works with ANY Retriever."""
from collections import defaultdict

from .metrics import mean, recall_at_k, reciprocal_rank
from .retrievers import Retriever

KS = (1, 3, 5)
DEPTH = 10   # how many chunks to fetch per question; MRR is measured over this many


def evaluate_retriever(retriever: Retriever, entries: list[dict], ks: tuple[int, ...] = KS,
                       depth: int = DEPTH) -> dict:
    """Retrieve for every ANSWERABLE question and score it.
    Unanswerable questions have no gold page, so they are counted but not scored here
    (they are tested by the answer evaluation on Day 12)."""
    depth = max(depth, max(ks))
    rows = []
    skipped = 0
    for e in entries:
        if not e["gold"]:
            skipped += 1
            continue
        hits = retriever.retrieve(e["question"], depth)
        retrieved = [(h.doc, h.page) for h in hits]
        gold = [(g["doc"], g["page"]) for g in e["gold"]]
        rows.append({
            "id": e["id"], "type": e["type"], "question": e["question"], "gold": gold,
            "retrieved": retrieved,
            **{f"recall@{k}": recall_at_k(retrieved, gold, k) for k in ks},
            "rr": reciprocal_rank(retrieved, gold),
        })
    return {"retriever": retriever.name, "ks": list(ks), "depth": depth, "skipped_unanswerable": skipped,
            "summary": summarize(rows, ks), "by_type": summarize_by_type(rows, ks), "rows": rows}


def summarize(rows: list[dict], ks: tuple[int, ...] = KS) -> dict:
    out = {"n": len(rows)}
    for k in ks:
        out[f"recall@{k}"] = round(mean([r[f"recall@{k}"] for r in rows]), 4)
    out["mrr"] = round(mean([r["rr"] for r in rows]), 4)
    return out


def summarize_by_type(rows: list[dict], ks: tuple[int, ...] = KS) -> dict:
    groups = defaultdict(list)
    for r in rows:
        groups[r["type"]].append(r)
    return {t: summarize(rs, ks) for t, rs in sorted(groups.items())}


def format_table(result: dict) -> str:
    ks = result["ks"]
    header = ["group", "n"] + [f"recall@{k}" for k in ks] + ["MRR"]
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]

    def row(name, s):
        cells = [name, str(s["n"])] + [f"{s[f'recall@{k}']:.3f}" for k in ks] + [f"{s['mrr']:.3f}"]
        return "| " + " | ".join(cells) + " |"

    lines.append(row("**all**", result["summary"]))
    for t, s in result["by_type"].items():
        lines.append(row(t, s))
    return "\n".join(lines)