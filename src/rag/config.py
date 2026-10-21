"""Every tunable setting in ONE place. Other modules import from here instead of hard-coding values.

Values that are secrets or differ per machine come from environment variables (.env).
LLM settings (provider, model, key, limits) are NOT here: llm.py reads them at call time on purpose,
so changing .env or a test's monkeypatch takes effect without re-importing anything.
"""
import os

from dotenv import load_dotenv

load_dotenv()  # reads .env if present; real environment variables win


def _int(name: str, default: int) -> int:
    return int(os.getenv(name, default))


# --- embeddings ---
EMBED_MODEL = "BAAI/bge-small-en-v1.5"   # 384-dimensional vectors, fast on CPU
# bge models want this sentence in front of SEARCH QUERIES only (never in front of documents).
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# --- chunking (tokens) ---
CHUNK_SIZE = _int("CHUNK_SIZE", 500)
CHUNK_OVERLAP = _int("CHUNK_OVERLAP", 50)

# --- retrieval ---
SEARCH_TOP_K = 5        # default k for /search
ASK_TOP_K = _int("ASK_TOP_K", 5)   # how many chunks the LLM gets to read in /ask

# --- vector database ---
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")   # ":memory:" = throwaway, for tests
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
COLLECTION = os.getenv("COLLECTION", f"chunks_{CHUNK_SIZE}")