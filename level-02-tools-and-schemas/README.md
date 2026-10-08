# Level 2 · Tools and Schemas

**Big idea:** a tool is a function with a **contract the model can read**. Clear names, typed arguments and useful error messages matter more than clever prompts.

**Ops Buddy gains:** `check_leave_balance`, `apply_leave`, `create_ticket` and `get_ticket_status`, with validated arguments. The finished code lives in [`ops_buddy/tools.py`](../ops_buddy/tools.py).

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `01_bad_vs_good_tool.py` | The same tool described badly and well | No |
| `02_validation_errors.py` | Bad arguments → helpful errors, never a crash | No |
| `03_tool_round_trip.py` | One tool call by hand: `tool_use` → run → `tool_result` → answer | Yes |
| `04_structured_output.py` | Pull a typed `LeaveRequest` out of an email with `messages.parse` | Yes |

## The round trip

```
YOU ──(question + tool list)──▶ MODEL
YOU ◀──── tool_use {name, input, id} ──── MODEL      the model only ASKS
YOU: run_tool(name, input)                           your code DOES it
YOU ──── tool_result {tool_use_id, content} ───▶ MODEL
YOU ◀──────────── final text ──────────────── MODEL
```

## Six rules for good tools

1. **Name = verb + noun**: `apply_leave`, not `leave` or `do_action`.
2. **The description says when to use it**, and what it does *not* do ("NOT approved yet").
3. **Type every argument**; use enums (`Literal`) for fixed choices and formats for dates.
4. **Validate before acting** (Pydantic). The model *will* send bad input.
5. **Errors explain the fix**: "Leave must be for a future date", not `ValueError`.
6. **Return only what the model needs**: small, readable JSON, not the whole database row.

## Try it

1. In `01`, give the bad tool to the model in `03` instead of the good one. What does it send?
2. Add a `cancel_leave(request_id)` tool to `ops_buddy/tools.py`: Pydantic model, handler, registry. Test it in `02` first.
3. In `04`, add an email in Hinglish ("kal chutti chahiye, tabiyat kharab hai"). Does extraction still work?
