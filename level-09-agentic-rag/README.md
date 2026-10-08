# Level 9 · Agentic RAG

**Big idea:** retrieval becomes **a tool the agent chooses** to use, retries and checks, instead of one fixed search before every answer.

**Ops Buddy gains:** searches the policy docs from the RAG series and cites them.

The policies live in [`ops_buddy/policies/`](../ops_buddy/policies/) (4 short Markdown files). The retriever in [`ops_buddy/policies.py`](../ops_buddy/policies.py) uses structure-based chunking + BM25, so it needs no embedding model. Swap in your hybrid retriever from the RAG series if you have one.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `00_search_policies.py` | The retriever alone, including a paraphrase it misses | **No** |
| `01_retrieval_as_tool.py` | `search_policies` as a tool next to the HR tools, with citations | Yes |
| `02_self_correcting_rag.py` | LangGraph: retrieve → grade → rewrite → retry → answer or give up | Yes |

## Classic RAG vs agentic RAG

| | Classic RAG | Agentic RAG |
|---|---|---|
| When to search | always, once | when the agent decides it needs to |
| Query | the user's words | the agent writes (and rewrites) it |
| Bad results | answered anyway | graded; retried or "I don't know" |
| Mixing sources | policy text only | policy + live tools (balance, tickets) |
| Cost | 1 search + 1 call | more calls; cap the retries |

## Try it

1. In `01`, ask "What's my sick leave balance?" Does the agent search the policies? Should it?
2. In `02`, set `MAX_TRIES = 1`. What happens to the "son has a fever" question?
3. Add a fifth policy file (e.g. `travel-policy.md`) and ask about it. No code changes needed. Why?
