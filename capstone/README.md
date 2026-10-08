# ★ Capstone · Add a Department to Ops Buddy

**Goal:** each student adds a new department, **Finance** (reimbursements) or **Facilities** (desks, rooms, repairs), to Ops Buddy, end to end, with tests.

You are not writing anything new. You are combining what Levels 2-14 taught, on a department nobody has built yet.

## Requirements

| # | Requirement | From level | Done when |
|---|---|---|---|
| 1 | 2-4 validated tools with clear descriptions and fixable errors | 2 | Bad arguments return helpful errors (show 3) |
| 2 | Decide what's a workflow vs agent, in writing (5 lines) | 1, 4 | Your README explains the choice |
| 3 | A specialist agent with only its own tools | 5, 11 | Plugged into the Level 11 front desk as `ask_finance` / `ask_facilities` |
| 4 | Answers policy questions with citations | 9 | Uses `ops_buddy/policies/` (add a policy file if needed) |
| 5 | Human approval for at least one risky action | 7, 13 | e.g. claims over Rs 10,000 pause for a manager |
| 6 | Remembers one useful preference per employee | 8 | e.g. preferred bank account nickname (never the number!) |
| 7 | Exposed as an MCP server | 10 | `01_mcp_client.py`-style script lists your tools |
| 8 | 15+ eval cases incl. 3 attacks, run with Level 12's runner | 12, 13 | Pass rate ≥ 85%, attacks held |
| 9 | Served through the Level 14 API | 14 | A streamed reply through `client.py` |

## Starter kit

`starter/` has a Finance skeleton to copy:

| File | What's in it |
|---|---|
| `finance_tools.py` | Fake claims data + one finished tool + two TODO tools |
| `finance_agent.py` | The specialist agent, ready to plug into Level 11 |
| `finance_cases.jsonl` | 3 eval cases in Level 12's format: add 12+ more |

```bash
python capstone/starter/finance_tools.py    # no API key needed
python capstone/starter/finance_agent.py
```

To run your cases with Level 12's runner, wrap your agent in a function `my_agent(text, employee_id) -> (answer, trace)`, with `trace` in the same format as `ops_buddy/agent.py`, and call `run_evals.main(agent=my_agent)`. For `create_agent` agents, build the trace from the `tool_calls` on the returned messages.

## Suggested timeline (2 weeks)

| Days | Milestone |
|---|---|
| 1-2 | Tools + workflow/agent decision + 5 eval cases |
| 3-5 | Specialist agent, policy search, plugged into the front desk |
| 6-7 | Approval gate + memory |
| 8-9 | MCP server + red-team cases |
| 10 | API + demo + 3-minute presentation: show one trace where it failed and how you fixed it |

## Grading rubric (100)

| Area | Points | Full marks looks like |
|---|---|---|
| Tools and schemas | 15 | Clear names, typed args, every error tells the model what to do |
| Agent design | 15 | Right workflow/agent split; specialist has least privilege |
| Safety | 20 | Approval gate works; 3 attacks held; no identity in tool args |
| Evals | 25 | 15+ cases, trajectory checks, pass rate reported honestly with failures explained |
| Production | 15 | Streams through the API, within budget |
| Demo | 10 | Shows a real failure trace and the fix |
