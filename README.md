# RAG App with an Eval Suite

Ask questions about a document collection and get answers with the source passage cited.
Retrieval and answer quality are measured on a 50-question test set, and every improvement
is recorded with before/after numbers.

**Status:** Day 5 of 28. Search works; answer generation comes next.

## Setup
Requires Python 3.10+ and Docker.

    python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    docker compose up -d                                   # starts Qdrant on localhost:6333

## Build the index
Put documents (PDF, HTML, Markdown, TXT) in `docs/`, then:

    python scripts/parse_docs.py                           # docs/ -> data/pages.jsonl
    python scripts/make_chunks.py --size 500 --overlap 50  # pages -> data/chunks_500.jsonl
    python scripts/build_index.py --size 500               # chunks -> embeddings -> Qdrant

## Run
    uvicorn rag.api:app --reload --app-dir src
    curl -X POST localhost:8000/search -H "content-type: application/json" \
         -d '{"query": "your question", "k": 3}'

Interactive API page: http://localhost:8000/docs

## Test
    pytest -q

## How it works
1. **Parse** documents into pages (keeping the page number for citations).
2. **Chunk** pages into overlapping ~500-token pieces with stable ids.
3. **Embed** each chunk with `BAAI/bge-small-en-v1.5` and store it in Qdrant.
4. **Search**: embed the question, return the nearest chunks with similarity scores.

## Project layout
    docs/       source documents (see sources.md)       src/rag/    the pipeline code
    data/       pages.jsonl, chunks_*.jsonl             scripts/    command-line tools
    evals/      test set and metrics (Week 2)           tests/      unit tests
    results/    experiment outputs                      notes/      learning log

## Results
| Experiment | recall@5 | MRR | Faithfulness |
|---|---|---|---|
| Baseline | TBD | TBD | TBD |