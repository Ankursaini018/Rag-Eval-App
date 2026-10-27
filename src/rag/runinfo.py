"""Describe exactly how an experiment was run, so a result file can be reproduced later."""
import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from . import config


def file_fingerprint(path: str | Path) -> str | None:
    """Short hash of a file's bytes. If the golden set changes, the hash changes."""
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12] if path.exists() else None


def git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def indexed_points(client, collection: str) -> int | None:
    try:
        return client.count(collection_name=collection, exact=True).count
    except Exception:
        return None


def describe_run(collection: str, golden_path: str | Path, client=None) -> dict:
    """Everything that affects the numbers (except the code itself, which `git_commit` identifies)."""
    return {
        "date": datetime.now().isoformat(timespec="seconds"),
        "git_commit": git_commit(),
        "python": sys.version.split()[0],
        "embed_model": config.EMBED_MODEL,
        "query_prefix": config.QUERY_PREFIX,
        "chunk_size_tokens": config.CHUNK_SIZE,
        "chunk_overlap_tokens": config.CHUNK_OVERLAP,
        "collection": collection,
        "chunks_in_collection": indexed_points(client, collection) if client is not None else None,
        "top_k_for_answers": config.ASK_TOP_K,
        "golden_file": Path(golden_path).name,
        "golden_sha256_12": file_fingerprint(golden_path),
    }