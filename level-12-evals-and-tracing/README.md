# Level 12 · Evals and Tracing

**Big idea:** **trace every step**, then score both the **final answer** and the **trajectory** (the sequence of tools it used, with what arguments). An agent can give the right answer the wrong way, for example by booking leave without checking the balance.

**Ops Buddy gains:** a test suite that runs on every change.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `dataset.jsonl` | 12 test cases (grow it to 40) | - |
| `scorers.py` | Answer checks, trajectory checks, LLM-as-judge | - |
| `test_scorers.py` | Unit tests for the scorers | **No** (`pytest level-12-evals-and-tracing -q`) |
| `run_evals.py` | Runs every case, prints a report, saves traces to `traces/` | Yes |

```bash
pytest level-12-evals-and-tracing -q
python level-12-evals-and-tracing/run_evals.py
python level-12-evals-and-tracing/run_evals.py apply-friday two-part   # just some cases
```

## Expected result

`security-other-employee` will probably **fail**: the tool accepts any `employee_id`, so Ops Buddy can read Rahul's leave balance for Priya. If it passes, the model refused on its own this time. Run it a few times: a defence that depends on the model's mood is not a defence. Level 13 fixes it in code, and then it passes every time.

## What a test case can check

| Field | Kind | Example |
|---|---|---|
| `answer_must_include` | answer | `["LR-"]` |
| `expect_tools` + `order` | trajectory | `["check_leave_balance", "apply_leave"]`, in order or any |
| `forbid_tools` | trajectory | `["apply_leave"]` when the leave type is unclear |
| `expect_args` | trajectory | `create_ticket` with `priority: high` |
| `forbid_args` | trajectory | never `check_leave_balance` for someone else's ID |
| `max_tool_calls` | trajectory | `0` for small talk |
| `judge` | LLM-as-judge | "Must NOT say the leave is approved" |

## Rules of thumb

- **Cheapest check that works.** Use string and trajectory checks first; reserve the judge for meaning ("did it ask which leave type?").
- **Reset state per case** (`data.reset()`), or one case's leave booking breaks the next.
- **Run each case 3-5 times** before trusting a pass rate: agents are not deterministic.
- **Every production bug becomes a new case.** That's how the suite grows from 12 to 40 and beyond.
- **Tracing:** each run is saved as JSONL in `traces/`. For the LangChain levels, set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` to see every step in LangSmith (Langfuse is an open-source alternative).

## Try it

1. Add 5 cases from real messages you'd expect, including one in Hinglish.
2. Remove "Check the balance first" from `apply_leave`'s description in `ops_buddy/tools.py`. Add `expect_tools: ["check_leave_balance", "apply_leave"]` to `apply-friday`. Does it still pass?
3. Make `run_evals.py` run each case 3 times and report flaky cases (pass sometimes, fail sometimes).
