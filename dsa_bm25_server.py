# -*- coding: utf-8 -*-
"""
FastAPI server for querying a BM25S index (DSA / Das Schwarze Auge).

- Expects an index directory that contains the BM25S files AND a sidecar meta.jsonl
  with one JSON object per document (same order or with integer 'doc_id').
- Returns RAW search results: for each hit you get {doc_index, score, meta}

Install:
    pip install fastapi uvicorn bm25s pydantic

Run:
    python dsa_bm25_server.py
    # or: uvicorn dsa_bm25_server:app --host 0.0.0.0 --port 8022

Query (example):
    curl -s -X POST "http://SERVER_OR_IP:8022/search" \
      -H "Content-Type: application/json" \
      -d "{\"query\":\"Horasischer Adel und Titel\",\"topk\":10,\"stopwords\":\"de\"}" | jq
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import bm25s  # pip install bm25s
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# -----------------------
# Config (env overridable)
# -----------------------
INDEX_DIR = os.environ.get("INDEX_DIR", "bm25_index")
DEFAULT_STOPWORDS = os.environ.get("STOPWORDS", None)  # e.g., "de"
PORT = int(os.environ.get("PORT", "8022"))

# -----------------------
# Load index + metadata
# -----------------------
index_path = Path(INDEX_DIR)
meta_path = index_path / "meta.jsonl"

if not index_path.exists():
    raise RuntimeError(f"Index folder not found: {index_path.resolve()}")

if not meta_path.exists():
    raise RuntimeError(f"Missing sidecar meta.jsonl: {meta_path.resolve()}")

# Load meta.jsonl
metas: List[Dict[str, Any]] = []
with meta_path.open("r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            metas.append(json.loads(line))

# If meta has integer 'doc_id', sort by it to align with index order.
if metas and isinstance(metas[0], dict) and "doc_id" in metas[0]:
    try:
        metas.sort(key=lambda m: int(m["doc_id"]))
    except Exception:
        # Fallback: keep file order
        pass

# Load BM25 retriever (we assume the index was built without storing the corpus)
retriever = bm25s.BM25.load(str(index_path), load_corpus=False)

# -----------------------
# API
# -----------------------
app = FastAPI(title="DSA BM25 API", version="1.0.0")


class SearchRequest(BaseModel):
    query: str
    topk: int = 10
    stopwords: Optional[str] = None  # e.g., "de"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "index_dir": str(index_path),
        "meta_docs": len(metas),
        "default_stopwords": DEFAULT_STOPWORDS,
    }


@app.post("/search")
def search(req: SearchRequest):
    try:
        sw = req.stopwords if req.stopwords is not None else DEFAULT_STOPWORDS
        q_tokens = bm25s.tokenize(req.query, stopwords=sw)
        docs, scores = retriever.retrieve(q_tokens, k=req.topk)  # shapes: (1, k)

        results: List[Dict[str, Any]] = []
        for doc_idx, score in zip(docs[0], scores[0]):
            di = int(doc_idx)
            meta = metas[di] if 0 <= di < len(metas) else {}
            results.append(
                {
                    "doc_index": di,          # raw index ID from BM25
                    "score": float(score),    # raw score
                    "meta": meta,             # raw meta doc (no formatting)
                }
            )

        return {
            "query": req.query,
            "topk": req.topk,
            "stopwords": sw,
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
