"""The retriever on its own: structure-based chunks + BM25. Same idea as the RAG series.

Run (no API key needed):  python level-09-agentic-rag/00_search_policies.py

Compare the last two queries: the same need in different words. Keyword search finds
"childcare emergencies" for the first and misses it for the paraphrase.
In 02, the agent fixes this by rewriting its own query.
"""

from ops_buddy.policies import CHUNKS, search

print(f"{len(CHUNKS)} chunks from {len({c['file'] for c in CHUNKS})} policy files\n")

for q in ["sick leave medical certificate", "Form HR-204", "can I stay home if my kid is unwell",
          "my son has a fever, can I log in from my flat today"]:
    print(f"QUERY: {q}")
    hits = search(q)
    for h in hits:
        print(f"   {h['score']:5.2f}  [{h['source']}]  {h['text'][:70]}...")
    if not hits:
        print("   (no results)")
    print()
