# -*- coding: utf-8 -*-
"""
Load a BM25S index and run queries against it. Pretty-print top-k hits.

Requires the index folder created by build_bm25_index.py
(which writes bm25 index files + meta.jsonl containing doc metadata).

Install:
    pip install bm25s[full] pandas

Usage (one-shot):
    python query_bm25.py --index-dir bm25_index --query "Horasischer Adel und Titel" --topk 10 --stopwords de

Usage (interactive shell if --query omitted):
    python query_bm25.py --index-dir bm25_index

Notes:
- We **built** the index with BM25() *without* passing corpus, so
  retrieve() returns **indices**; we map indices → meta.jsonl to format results.
  (If you build with BM25(corpus=...), retrieve returns docs; see bm25s docs.)
"""
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

import bm25s  # pip install bm25s[full]

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Query a BM25S index built from dsaEntitäten.csv")
    ap.add_argument("--index-dir", default="bm25_index", type=str,
                    help="Directory containing the BM25S index and meta.jsonl")
    ap.add_argument("--query", default=None, type=str,
                    help="Query string. If omitted, enters interactive loop.")
    ap.add_argument("--topk", default=10, type=int, help="Number of results to return")
    ap.add_argument("--stopwords", default=None, type=str, help="Stopword language for bm25s.tokenize (e.g., 'de')")
    return ap.parse_args()

def load_meta(meta_path: Path) -> List[Dict[str, Any]]:
    metas: List[Dict[str, Any]] = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            metas.append(json.loads(line))
    # Ensure doc_id ordering matches index
    metas.sort(key=lambda m: m["doc_id"])
    return metas

def retrieve(retriever: bm25s.BM25, metas: List[Dict[str, Any]],
             query: str, topk: int, stopwords=None) -> List[Tuple[int, float, Dict[str, Any]]]:
    """
    Returns list of (rank, score, meta_dict) for topk hits.
    """
    q_tokens = bm25s.tokenize(query, stopwords=stopwords)
    # Since we built the index with BM25() (no corpus passed), retrieve() returns INDICES + SCORES.
    # API on docs: docs, scores = retriever.retrieve(...); here docs will be indices (2D array).
    docs, scores = retriever.retrieve(q_tokens, k=topk)
    # docs, scores have shape (1, topk) for a single query
    hits = []
    for rank, (doc_id, score) in enumerate(zip(docs[0], scores[0]), start=1):
        m = metas[int(doc_id)]
        hits.append((rank, float(score), m))
    return hits

def format_hit(rank: int, score: float, meta: Dict[str, Any]) -> str:
    """
    Pretty print one hit:
    - Top N:
    - EntityName: ...
    - Beschreibung: ...
    - Fakten:
        - <statement> — Quelle: <source>
    """
    lines = []
    lines.append(f"Top {rank}  (Score: {score:.4f})")
    lines.append(f"EntityName: {meta.get('entity_name', '')}")
    lines.append(f"Beschreibung: {meta.get('description', '')}")
    lines.append("Fakten:")
    facts = meta.get("facts", [])
    if not isinstance(facts, list):
        facts = []
    if not facts:
        lines.append("  (keine Fakten)")
    else:
        for f in facts:
            if not isinstance(f, dict):
                continue
            st = f.get("statement", "")
            so = f.get("source", "")
            if st:
                if so:
                    lines.append(f"  - {st} — Quelle: {so}")
                else:
                    lines.append(f"  - {st}")
    return "\n".join(lines)

def interactive_loop(retriever: bm25s.BM25, metas: List[Dict[str, Any]], stopwords, topk: int):
    print("BM25S Suche – tippe eine Query (oder 'exit'):")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return
        if not q or q.lower() in {"exit", "quit"}:
            print("Bye.")
            return
        hits = retrieve(retriever, metas, q, topk=topk, stopwords=stopwords)
        print()
        for rank, score, meta in hits:
            print(format_hit(rank, score, meta))
            print("-" * 80)

def main():
    args = parse_args()
    index_dir = Path(args.index_dir)
    if not index_dir.exists():
        raise SystemExit(f"Index folder not found: {index_dir}")

    meta_path = index_dir / "meta.jsonl"
    if not meta_path.exists():
        raise SystemExit(f"Missing sidecar meta.jsonl in index folder: {meta_path}")

    metas = load_meta(meta_path)

    # Load BM25 index (we didn't store corpus, so load_corpus=False is fine)
    retriever = bm25s.BM25.load(str(index_dir), load_corpus=False)

    if args.query:
        hits = retrieve(retriever, metas, args.query, topk=args.topk, stopwords=args.stopwords)
        for rank, score, meta in hits:
            print(format_hit(rank, score, meta))
            print("-" * 80)
    else:
        interactive_loop(retriever, metas, stopwords=args.stopwords, topk=args.topk)

if __name__ == "__main__":
    main()
