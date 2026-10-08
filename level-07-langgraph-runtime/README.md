# Level 7 · LangGraph Runtime

**Big idea:** **checkpoints** save state at every step, so a run can **pause for a human** and resume later, even after a restart. Streaming shows progress while it works.

**Ops Buddy gains:** waits for a manager's approval before granting leave.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `01_pause_for_approval.py` | `interrupt()` + `Command(resume=...)` with an in-memory checkpointer | **No** |
| `02_survive_restart.py` | Pause in one process, resume in another (SQLite) | **No** |
| `03_streaming.py` | Step events + token-by-token text | Yes |
| `04_approval_middleware.py` | `HumanInTheLoopMiddleware` on `apply_leave`; you approve in the terminal | Yes |

Try the restart demo as three separate commands:

```bash
python level-07-langgraph-runtime/02_survive_restart.py request Priya 2026-10-09
python level-07-langgraph-runtime/02_survive_restart.py pending
python level-07-langgraph-runtime/02_survive_restart.py approve <thread_id>
```

## How pause and resume work

```
invoke(input, thread_id=T) ─▶ submit ─▶ manager_review ─▶ interrupt()  ⏸  state saved under T
                                                                          │
                     (minutes, days, or a server restart later)           │
                                                                          ▼
invoke(Command(resume=answer), thread_id=T) ─────────▶ manager_review re-runs, interrupt() returns answer ─▶ finalize
```

## Three rules

1. **No checkpointer, no pause.** `interrupt()` needs a checkpointer and a `thread_id`.
2. **The interrupted node runs again from the top on resume.** Don't put side effects (emails, DB writes) before `interrupt()` in the same node.
3. **In-memory is for demos.** Use SQLite or Postgres checkpointers for anything that must survive a restart.

## Try it

1. In `01`, resume with `{"approved": False, "note": "release week"}`.
2. In `02`, start two requests and approve only one. Run `pending` again.
3. Move a `print("EMAIL SENT")` *above* `interrupt()` in `01`'s `manager_review`. How many times does it print? Why is that a bug?
