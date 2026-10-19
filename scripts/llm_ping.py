"""Check that your API key and model work.   Run:  python scripts/llm_ping.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rag.llm import LLMConfigError, complete  # noqa: E402

if __name__ == "__main__":
    try:
                r = complete("You are a terse assistant.", "Reply with exactly one word: hello")
    except LLMConfigError as e:
        sys.exit(f"Setup problem: {e}")
    print(f"reply: {r.text!r}   tokens in/out: {r.input_tokens}/{r.output_tokens}")
    if not r.text.strip():
        print("The reply is EMPTY. With a reasoning model, raise LLM_MAX_TOKENS in .env (e.g. 1500) "
              "and set LLM_REASONING_EFFORT=low.")