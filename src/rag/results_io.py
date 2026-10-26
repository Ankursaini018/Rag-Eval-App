"""Save and export evaluation results."""
import json
from pathlib import Path


def save_result(result: dict, path: str | Path) -> Path:
    """Write the full result (summary, per-type numbers, every question's row) as readable JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path