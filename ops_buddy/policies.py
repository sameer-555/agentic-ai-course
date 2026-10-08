"""The HR policy corpus from the RAG series, with a small keyword search.

Chunking: one chunk per '##' section, with the heading path kept as the source
(structure-based chunking). Search: BM25, so this runs with no embedding model.
Swap in your own dense or hybrid retriever from the RAG series if you have one.
"""

import re
from pathlib import Path

from rank_bm25 import BM25Okapi

POLICY_DIR = Path(__file__).parent / "policies"


def load_chunks():
    chunks = []
    for path in sorted(POLICY_DIR.glob("*.md")):
        title, section, lines = None, None, []
        for line in path.read_text().splitlines() + ["## <end>"]:
            if line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("## "):
                if section and lines:
                    chunks.append({"source": f"{title} > {section}", "file": path.name,
                                   "text": " ".join(lines).strip()})
                section, lines = line[3:].strip(), []
            elif line.strip():
                lines.append(line.strip())
    return chunks


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9-]*", text.lower())  # keeps IDs like hr-204 whole


CHUNKS = load_chunks()
_bm25 = BM25Okapi([tokenize(f"{c['source']} {c['text']}") for c in CHUNKS])


def search(query: str, k: int = 3) -> list[dict]:
    """Return the top-k chunks for a query, best first, with a score."""
    scores = _bm25.get_scores(tokenize(query))
    best = sorted(range(len(CHUNKS)), key=lambda i: scores[i], reverse=True)[:k]
    return [{**CHUNKS[i], "score": round(float(scores[i]), 2)} for i in best if scores[i] > 0]
