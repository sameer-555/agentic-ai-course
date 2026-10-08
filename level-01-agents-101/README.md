# Level 1 · Agents 101

**Big idea:** an agent is a **model + tools + a loop**. In a **workflow**, your code decides each step. In an **agent**, the model decides. Use the simplest one that works.

**Ops Buddy gains:** a job description, and a decision about which parts should be a workflow.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `01_single_call.py` | One call, no tools. The model can't know the leave balance. | Yes |
| `02_workflow.py` | Code picks the steps: classify → look up → reply. Breaks on a two-part question. | Yes |
| `03_agent.py` | The model picks tools in a loop. Handles the two-part question. | Yes |

```bash
python level-01-agents-101/01_single_call.py
python level-01-agents-101/02_workflow.py
python level-01-agents-101/03_agent.py
```

## The agent loop

```
user message
     │
     ▼
┌──────────┐   wants a tool?   ┌───────────┐
│  MODEL   │ ────── yes ─────▶ │  RUN TOOL │
│ (decide) │ ◀── result ────── │  (act)    │
└──────────┘                   └───────────┘
     │ no
     ▼
final answer
```

## Four questions to decide: workflow or agent?

1. **Can you write the steps down in advance?** If yes, it's a workflow.
2. **Does each next step depend on what the last one revealed, in ways you can't list?** If yes, it needs an agent.
3. **How bad is a wrong action?** The higher the cost, the more you want a fixed path, or an agent that must get human approval (Level 7).
4. **How tight are the time and cost budgets?** Every loop iteration is another model call.

## Try it

1. **Predict:** before running `01_single_call.py`, write down what you think the model will answer. Were you right?
2. In `02_workflow.py`, add a new intent `ticket_status` that looks up `IT-3001`. How many places did you have to change?
3. Sort these into workflow or agent, using the four questions:
   - Send a welcome email to every new joiner on their first day
   - "My VPN is broken and I have a demo in 20 minutes, help"
   - Monthly leave report for each manager
   - "Plan my leave around the team's release dates"
