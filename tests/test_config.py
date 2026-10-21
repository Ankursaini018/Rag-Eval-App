from rag import config
from rag.chunk import chunk_page
from rag.embed import MODEL_NAME, QUERY_PREFIX


def test_modules_use_the_values_from_config():
    assert MODEL_NAME == config.EMBED_MODEL
    assert QUERY_PREFIX == config.QUERY_PREFIX
    assert chunk_page.__defaults__[:2] == (config.CHUNK_SIZE, config.CHUNK_OVERLAP)


def test_defaults_are_sane():
    assert 0 <= config.CHUNK_OVERLAP < config.CHUNK_SIZE
    assert config.ASK_TOP_K >= 1 and config.SEARCH_TOP_K >= 1
    assert config.COLLECTION.startswith("chunks_")