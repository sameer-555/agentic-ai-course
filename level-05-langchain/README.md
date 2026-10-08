# Level 5 · LangChain 1.0

**Big idea:** `create_agent` is the standard way to build an agent in LangChain 1.0. **Middleware** (hooks before and after model and tool calls) replaces the custom code you wrote in Level 3.

**Ops Buddy gains:** rebuilt in far less code, with a step limit and auto-summarised history.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `01_create_agent.py` | Level 3's loop in ~10 lines | Yes |
| `02_middleware.py` | Step limit, summarisation, and two custom hooks | Yes |

## Hand-written loop → LangChain

| Level 3 (by hand) | LangChain 1.0 |
|---|---|
| `TOOLS` list + Pydantic schemas | `@tool` functions (`ops_buddy/lc_tools.py`) |
| `for step in range(MAX_STEPS)` | `create_agent(...)` runs the loop |
| `MAX_STEPS` | `ModelCallLimitMiddleware(run_limit=...)` |
| trimming old messages | `SummarizationMiddleware(...)` |
| print statements in the loop | `@before_model`, `@wrap_tool_call` |
| `messages` list | `result["messages"]` |

## Outdated tutorials: watch out

If a tutorial uses `AgentExecutor`, `initialize_agent`, `LLMChain` or `from langchain.chains import ...`, it is **pre-1.0**. Those APIs moved to the separate `langchain-classic` package. Use `create_agent`.

## Names you'll hear

Same concepts, different syntax: OpenAI Agents SDK, Claude Agent SDK, Pydantic AI, CrewAI, Google ADK, Microsoft Agent Framework. Learn one stack deeply; the ideas transfer.

## Try it

1. Set `run_limit=1` in `02`. What does the agent return when it hits the limit?
2. Write a `@wrap_tool_call` middleware that blocks `apply_leave` on weekends (return an error message instead of calling `handler`).
3. Compare line counts: `level-03-agent-by-hand/agent.py` vs `01_create_agent.py`. What did you give up in exchange?
