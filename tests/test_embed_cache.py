import numpy as np

from rag import embed


def test_cache_reuses_and_invalidates(tmp_path, monkeypatch):
    calls = []

    def fake(texts, batch_size=32):
        calls.append(len(texts))
        return np.ones((len(texts), 4), dtype=np.float32)

    monkeypatch.setattr(embed, "embed_texts", fake)
    p = tmp_path / "v.npz"
    embed.embed_cached(["a", "b"], p)
    embed.embed_cached(["a", "b"], p)      # same texts -> loaded from disk, no new call
    assert calls == [2]
    embed.embed_cached(["a", "b", "c"], p)  # texts changed -> re-embed
    assert calls == [2, 3]