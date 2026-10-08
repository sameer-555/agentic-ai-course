# Agentic AI: The Course · Example Code

Working examples for every level of **Agentic AI: The Course Map**: 14 levels plus a capstone, taking fresh CS graduates from "what is an agent?" to shipping a tested, guarded agent.

All levels grow **one agent, Ops Buddy**: the internal helpdesk agent for the same company whose HR policies students chunked, embedded and searched in the RAG series. Each level starts with something Ops Buddy can't do yet and ends with code that does it.

## Setup (once)

```bash
cd agentic-ai-course
python3 -m venv .venv && source .venv/bin/activate      # Python 3.10+
pip install -e .                                         # installs the shared ops_buddy package + all libraries
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env               # put your real key here; .env is git-ignored
```

Run every example **from this folder**, e.g. `python level-03-agent-by-hand/agent.py`.

**No API key yet?** Start with the examples marked **offline** below. They run free and show the core ideas.

```bash
pytest -q          # offline tests for the scorers (L12) and the API (L14)
```

## The levels

| Phase | Level | Big idea | Ops Buddy gains | Offline examples |
|---|---|---|---|---|
| **1 · Foundations** | [1 · Agents 101](level-01-agents-101/) | Model + tools + loop; workflow vs agent | A job description | - |
| | [2 · Tools and schemas](level-02-tools-and-schemas/) | A tool is a contract the model can read | Validated leave and ticket tools | `01`, `02` |
| | [3 · Agent by hand](level-03-agent-by-hand/) | The loop in ~60 lines; step limits, errors | Answers "how many leaves do I have?" | - |
| | [4 · Workflow patterns](level-04-workflow-patterns/) | Chaining, routing, parallel, orchestrator-workers, evaluator-optimizer | Routes HR vs IT; checks drafts | - |
| **2 · LangChain stack** | [5 · LangChain 1.0](level-05-langchain/) | `create_agent` + middleware | Rebuilt in far less code | - |
| | [6 · LangGraph basics](level-06-langgraph-basics/) | State, nodes, edges | Leave process as a graph | `01` |
| | [7 · LangGraph runtime](level-07-langgraph-runtime/) | Checkpoints, interrupts, streaming | Waits for manager approval | `01`, `02` |
| | [8 · Memory and context](level-08-memory-and-context/) | Short vs long-term memory; context engineering | Remembers preferences | - |
| | [9 · Agentic RAG](level-09-agentic-rag/) | Retrieval as a tool; grade and retry | Searches and cites policies | `00` |
| **3 · Connect & scale** | [10 · MCP tools](level-10-mcp/) | One standard plug for tools | Uses ticketing + calendar servers | `01` |
| | [11 · Multi-agent](level-11-multi-agent/) | Supervisor, handoffs, and when not to | Front desk + HR/IT specialists | - |
| **4 · Production** | [12 · Evals and tracing](level-12-evals-and-tracing/) | Score the answer *and* the trajectory | A test suite | `test_scorers.py` |
| | [13 · Guardrails](level-13-guardrails/) | Least privilege + approval, in code | Survives a red-team session | `01`, `03` |
| | [14 · Ship it](level-14-ship-it/) | API, streaming, budgets, retries | Live, with a cost cap | `test_app.py` |
| ★ | [Capstone](capstone/) | Put it all together | A new department, end to end | `starter/finance_tools.py` |

## What's shared

```
ops_buddy/
  data.py        fake employees, tickets, leave requests (reset() before each test)
  tools.py       the Level 2 tools: Pydantic contracts + handlers + safe run_tool()
  agent.py       the Level 3 loop with guard rails, reused by Levels 12-14
  lc_tools.py    the same tools as LangChain @tool functions (Level 5+)
  policies/      4 HR/IT policy documents (the RAG corpus)
  policies.py    structure-based chunking + BM25 search (Level 9)
  config.py      MODEL (default claude-opus-5; override with OPS_BUDDY_MODEL) + clients
```

The employee database is fake and fixed: "today" is always **Monday, 5 October 2026**, and the logged-in user is usually **Priya Sharma (E1042)**, so every run and every eval behaves the same.

## Each level folder

- `README.md`: the big idea, a diagram, a comparison table, and **Try it** exercises
- numbered example files, in teaching order; each file's docstring says how to run it and what to watch for

## A note on versions

Agent libraries change fast. These examples were written against `anthropic 1.12`, `langchain 1.4`, `langgraph 1.2` and `mcp 1.30` (October 2026). If a tutorial online uses `AgentExecutor` or `initialize_agent`, it's pre-1.0 and outdated.
