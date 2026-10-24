"""Score a retriever on the golden set (recall@1/3/5 and MRR). Needs Qdrant running for 'vector'.
Run:  python scripts/run_retrieval_eval.py --retriever vector
      python scripts/run_retrieval_eval.py --retriever vector --collection chunks_500 --show-misses"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.golden import load_golden, validate_entries  # noqa: E402
from rag.retrieval_eval import DEPTH, evaluate_retriever, format_table  # noqa: E402
from rag.retrievers import build_retriever  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--retriever", default="vector")
    ap.add_argument("--collection", default=None, help="Qdrant collection (default: from config)")
    ap.add_argument("--golden", default=str(ROOT / "data" / "golden.jsonl"))
    ap.add_argument("--depth", type=int, default=DEPTH, help="chunks fetched per question")
    ap.add_argument("--show-misses", action="store_true", help="list questions with recall@5 below 1")
    args = ap.parse_args()

    entries = load_golden(args.golden)
    problems = validate_entries(entries)
    if problems:
        sys.exit("golden set is invalid, fix it first:\n  " + "\n  ".join(problems))

    result = evaluate_retriever(build_retriever(args.retriever, args.collection), entries, depth=args.depth)
    print(f"retriever: {result['retriever']}   depth: {result['depth']}   "
          f"scored: {result['summary']['n']}   skipped (unanswerable): {result['skipped_unanswerable']}\n")
    print(format_table(result))
    if args.show_misses:
        print("\nQuestions where not every gold page is in the top 5:")
        for r in result["rows"]:
            if r["recall@5"] < 1:
                print(f"  {r['id']} [{r['type']}] recall@5={r['recall@5']:.2f}  {r['question']}")