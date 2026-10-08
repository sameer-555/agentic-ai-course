# Level 3 · Agent by Hand

**Big idea:** the agent loop is about 60 lines of Python: **call the model → run the tool → feed back the result → stop**. Add step limits and error handling, and you have a real agent. No framework needed.

**Ops Buddy gains:** answers "how many leaves do I have left?" end to end, and can apply for leave or raise a ticket.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `agent.py` | The complete loop, worked example | Yes |
| `02_guard_rails.py` | A tool that always crashes: the agent survives and stops | Yes |
| `03_your_turn.py` | Half-done loop with 3 TODOs for students | Yes |

## How the messages list grows

```
[0] user       "Take this Friday off as casual leave"
[1] assistant  tool_use  check_leave_balance {employee_id: E1042}
[2] user       tool_result {casual: 4, sick: 6, earned: 12}
[3] assistant  tool_use  apply_leave {date: 2026-10-09, type: casual}
[4] user       tool_result {request_id: LR-5531, status: pending_manager_approval}
[5] assistant  "Done! Your request LR-5531 is waiting for your manager."   ← no tool_use → STOP
```

The model has no memory between calls. **The messages list *is* its memory**, and it is sent in full every step.

## Guard rails (see `ops_buddy/agent.py`)

| Guard rail | Stops |
|---|---|
| `MAX_STEPS` | infinite loops |
| `try/except` around tools | one broken tool killing the whole run |
| `is_error: true` on tool results | the model treating an error as data |
| repeat-call counter | the same failing call tried again and again |
| token budget | a single question costing a fortune |

## Common crashes

- **Forgot to append the assistant message** → API error: `tool_result` with no matching `tool_use`.
- **Sent tool results in separate user messages** → works, but the model stops making parallel calls.
- **Returned a Python object, not a string** → `content` must be a string (use `json.dumps`).

## Try it

1. Finish `03_your_turn.py`.
2. Print `len(messages)` and the input tokens each step. How fast does the cost grow?
3. Ask "Apply casual leave for yesterday". Read the trace: how did the agent recover?
