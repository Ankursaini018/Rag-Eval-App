"""Token positions and counts.

A 'token' is the unit an embedding model reads: a word or a piece of a word ('tokenization' ->
'token' + '##ization'). Models have a hard limit on tokens per input (bge: 512), so chunk size
must be measured in tokens, not words or characters.

We ask the tokenizer for each token's SPAN (start and end character position in the original text).
Chunks are then cut out of the original text by position, so capital letters, line breaks and
punctuation are kept exactly as written.
"""
import os
import re
import sys
from functools import lru_cache

from .embed import MODEL_NAME


class WordTokenizer:
    """Fallback: one 'token' per whitespace-separated word. Only an approximation (real token
    counts are about 1.3x higher), used when the model's tokenizer cannot be loaded."""

    name = "words"

    def spans(self, text: str) -> list[tuple[int, int]]:
        return [m.span() for m in re.finditer(r"\S+", text)]


class HFTokenizer:
    """The real tokenizer of the embedding model (Hugging Face 'fast' tokenizer)."""

    def __init__(self, hf_tokenizer, name: str):
        self._tok = hf_tokenizer
        self.name = name

    @classmethod
    def load(cls, model_name: str = MODEL_NAME) -> "HFTokenizer":
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(model_name)
        tok.model_max_length = 10**9  # we do the cutting ourselves; silence the 'too long' warning
        return cls(tok, model_name)

    def spans(self, text: str) -> list[tuple[int, int]]:
        enc = self._tok(text, add_special_tokens=False, return_offsets_mapping=True)
        return [(int(a), int(b)) for a, b in enc["offset_mapping"]]


@lru_cache(maxsize=1)
def get_tokenizer():
    if os.getenv("TOKENIZER") == "words":
        return WordTokenizer()
    try:
        return HFTokenizer.load()
    except Exception as e:  # offline, model not downloaded yet, etc.
        print(f"WARNING: could not load the {MODEL_NAME} tokenizer ({type(e).__name__}). "
              "Falling back to word counting: chunk sizes will be approximate.", file=sys.stderr)
        return WordTokenizer()


def count_tokens(text: str, tokenizer=None) -> int:
    return len((tokenizer or get_tokenizer()).spans(text))