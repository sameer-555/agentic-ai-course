# Level 14 · Ship It

**Big idea:** an agent in production is the same loop, plus what's needed around it: **serving behind an API, streaming, token budgets, retries and failure handling**.

**Ops Buddy gains:** it's live, with streaming responses and a cost cap.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `app.py` | FastAPI + Server-Sent Events, secured tools, budgets, retries, friendly errors | Yes (to chat) |
| `client.py` | Terminal client that prints tool steps and streamed text | - |
| `test_app.py` | Auth, cost cap and health tests | **No** (`pytest level-14-ship-it -q`) |
| `Dockerfile` | Container image for the service | - |

```bash
uvicorn app:app --app-dir level-14-ship-it --port 8000        # terminal 1
python level-14-ship-it/client.py "Book casual leave this Friday"   # terminal 2
python level-14-ship-it/client.py --employee E1077 "Status of IT-3001?"
```

## What wraps the loop

```
 request ─▶ auth (who is this?) ─▶ daily cost cap? ─▶ AGENT LOOP ─────────────────▶ SSE stream
                                                       │  per step:                   event: tool
                                                       │   stream model text ───────▶ event: text
                                                       │   add cost to SPEND           event: done
                                                       │   token budget / step limit   event: error
                                                       │   run secured tools
                                                       └─ SDK retries 429/5xx with backoff
```

## Production checklist

| Concern | Here | In a real deployment |
|---|---|---|
| Identity | `X-Employee-Id` header (demo only!) | SSO / JWT from your login system |
| Streaming | SSE via `StreamingResponse` | same; WebSockets if you need two-way |
| Retries | `Anthropic(max_retries=3, timeout=60)` | + a circuit breaker; fallback message |
| Cost | per-request token budget + per-day cap | + alerts, per-team budgets, dashboards |
| State | in-memory `SESSIONS` | Redis / Postgres; LangGraph checkpointer (Level 7) |
| Long tasks | run inside the request | a job queue (Celery, RQ) or a durable runtime (Temporal) |
| Quality | Level 12 evals | evals in CI on every change + sampled production traces |
| Versioning | one model constant | pin model + prompt version; log both with every trace |

## Try it

1. Set `DAILY_COST_CAP_USD = 0.01` and chat until you hit the cap. Is the message friendly?
2. Ask two questions with the same `--session`. Then a different session. Which remembers?
3. Add a `/feedback` endpoint (thumbs up/down + session id) and save it to a file: those become new eval cases.
