# Level 11 · Multi-Agent

**Big idea:** **supervisors, handoffs and subagents** with their own context. Just as important: knowing when **one agent is the better design**.

**Ops Buddy gains:** a front-desk agent that hands work to HR and IT specialists.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `specialists.py` | HR and IT agents, each with only its own tools | (module) |
| `01_supervisor_subagents.py` | Front desk calls specialists as tools and writes one reply | Yes |
| `02_handoffs.py` | Triage hands the whole conversation to one specialist | Yes |

## Supervisor vs handoff

```
SUPERVISOR (01)                              HANDOFF (02)
user ─▶ front_desk ─▶ ask_hr ─▶ hr_agent      user ─▶ triage ─▶ hr_agent ─▶ user
            │     ◀── answer ──┘                         └──▶ it_agent ─▶ user
            ├───▶ ask_it ─▶ it_agent
            ▼     ◀── answer ──┘
          one reply
```

| | Supervisor | Handoff |
|---|---|---|
| Who replies | front desk | the specialist |
| Mixed HR+IT message | handled (calls both) | only one side gets handled |
| Model calls | more | fewer |
| Context | each subagent starts clean | specialist sees the whole chat |

## When NOT to go multi-agent

Use **one agent** unless you have a real reason to split:

- **Too many tools** for one prompt (roughly 15-20+), or tools that confuse each other
- **Different permissions**: the IT agent must never touch leave data
- **Context overload**: one subtask reads lots of text that the rest doesn't need
- **Separate teams** own separate agents

Every extra agent adds latency, cost, and a new place for instructions to get lost in translation. Ops Buddy with 4 tools does *not* need this; it's here so you recognise the pattern.

## Names you'll hear

- **A2A (Agent2Agent):** a protocol for agents from *different companies or systems* to talk. MCP is agent-to-tool; A2A is agent-to-agent. Rare in a first job.
- **Deep agents** (LangChain Deep Agents, Claude Agent SDK): harnesses that bundle planning, a filesystem, subagents and memory for long tasks. Built from Levels 5-11.

## Try it

1. Send the stolen-laptop message to `02_handoffs.py`. What gets dropped?
2. In `01`, make `_run` return the full message history instead of the last message. Watch the front desk's token count grow.
3. **Boss level:** add a `finance_agent` (reimbursements, using Form HR-204/209 from the policies) to both patterns.
