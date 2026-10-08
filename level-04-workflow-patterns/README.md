# Level 4 · Workflow Patterns

**Big idea:** most "agent" problems are solved by five reusable shapes, where **your code owns the control flow**. Reach for a full agent only when none of these fit.

**Ops Buddy gains:** routes HR vs IT questions; drafts a reply and checks it before sending.

## The five patterns

| # | File | Shape | Use when |
|---|---|---|---|
| 1 | `01_prompt_chaining.py` | A → gate → B | Fixed steps, each easier than the whole |
| 2 | `02_routing.py` | classify → one of N handlers | Inputs fall into clear categories |
| 3 | `03_parallelization.py` | N calls at once → combine | Independent checks (sectioning) or more confidence (voting) |
| 4 | `04_orchestrator_workers.py` | model plans subtasks → workers → synthesise | Subtasks depend on the input and can't be listed in advance |
| 5 | `05_evaluator_optimizer.py` | write → grade → rewrite (capped) | Clear criteria, first drafts often miss |

All five need an API key. Run from the course root, e.g. `python level-04-workflow-patterns/02_routing.py`.

```
1 CHAINING        in ─▶ [LLM] ─▶ gate ─▶ [LLM] ─▶ out
2 ROUTING         in ─▶ [classify] ─┬─▶ [HR]
                                    ├─▶ [IT]
                                    └─▶ [other]
3 PARALLEL        in ─┬─▶ [check A] ─┐
                      ├─▶ [check B] ─┼─▶ combine
                      └─▶ [check C] ─┘
4 ORCH-WORKERS    in ─▶ [planner] ─▶ worker × N (decided at run time) ─▶ [synthesiser]
5 EVAL-OPTIMIZER  [writer] ⇄ [grader]   (max 3 rounds)
```

## Workflow vs agent, again

In all five, the *code* decides what happens next. In Level 3's agent, the *model* decides. Workflows are cheaper, faster and easier to test, so prefer them when the steps are known.

## Try it

1. In `02_routing.py`, send urgent IT messages to a handler that also says "I'm raising a high-priority ticket".
2. In `05`, remove the `MAX_ROUNDS` cap and make the criteria impossible. What would happen in production?
3. Combine patterns: route first (2), then run the evaluator-optimizer (5) only on HR replies.
