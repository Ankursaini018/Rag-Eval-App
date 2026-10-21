"""The web API.   Run:  uvicorn rag.api:app --reload --app-dir src     then open http://localhost:8000/docs"""
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import ASK_TOP_K, SEARCH_TOP_K
from .generate import answer_question
from .llm import LLMConfigError
from .search import search

log = logging.getLogger("rag.api")
app = FastAPI(title="RAG app with evals")


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    k: int = Field(default=SEARCH_TOP_K, ge=1, le=20)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


@app.post("/search")
def search_endpoint(req: SearchRequest) -> dict:
    """Return the k chunks closest in meaning to the query. (A plain `def`, not `async def`:
    embedding blocks the CPU, and FastAPI runs plain functions in a thread pool for us.)"""
    try:
        hits = search(req.query, req.k)
    except Exception:
        log.exception("search failed")
        raise HTTPException(status_code=503, detail="search backend unavailable")   # no internals leaked
    return {"query": req.query, "k": req.k, "hits": [h.to_dict() for h in hits]}


@app.post("/ask")
def ask_endpoint(req: AskRequest) -> dict:
    """Search for relevant chunks, then let the LLM answer from them."""
    try:
        hits = search(req.question, ASK_TOP_K)
    except Exception:
        log.exception("search failed")
        raise HTTPException(status_code=503, detail="search backend unavailable")
    try:
        out = answer_question(req.question, hits)
    except LLMConfigError as e:
        log.error("LLM not configured: %s", e)           # the message tells YOU what to fix; clients don't see it
        raise HTTPException(status_code=500, detail="the language model is not configured on the server")
    except Exception:
        log.exception("answer generation failed")
        raise HTTPException(status_code=503, detail="answer generation failed")
    return {"question": req.question, "answer": out["answer"], "refused": out["refused"],
            "citations": out["citations"], "retrieved": [h.to_dict() for h in hits]}