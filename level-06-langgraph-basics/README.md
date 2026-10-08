# Level 6 · LangGraph Basics

**Big idea:** **state, nodes and edges**. The agent's flow becomes an explicit graph you can read, draw and test, instead of a loop where the model decides everything.

**Ops Buddy gains:** the leave-request process as a graph with clear branches.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `leave_graph.py` | The graph definition: state, 6 nodes, 1 conditional edge, 1 reducer | (module) |
| `01_graph_no_llm.py` | Runs the graph with a keyword parser and prints it as Mermaid | **No** |
| `02_llm_in_a_node.py` | Swaps only the parse node for an LLM | Yes |

```
START → parse → check_balance ─┬─ enough ──────▶ submit ──┐
                               ├─ none left ───▶ reject ──┼─▶ reply → END
                               └─ missing info ▶ ask_user ┘
```

## The four words

| Word | Meaning | In `leave_graph.py` |
|---|---|---|
| **State** | A typed dict shared by all nodes | `LeaveState` |
| **Node** | A function: state in, partial update out | `check_balance`, `submit`, ... |
| **Edge** | What runs next: fixed, or chosen by a function | `add_edge`, `add_conditional_edges` |
| **Reducer** | How an update merges into state (default: overwrite) | `log: Annotated[list, operator.add]` appends |

## Where Level 5 fits

`create_agent` from Level 5 *is* a LangGraph graph with two nodes (model, tools) and a loop edge. Here you drop down a level to choose the nodes and edges yourself.

## Try it

1. Add an `earned` rule: earned leave needs 7 days' notice (see `ops_buddy/policies/leave-policy.md`). Add a node and a branch.
2. Write a pytest test for `route_after_balance`. No API key needed: it's just a function.
3. Remove the `operator.add` reducer from `log`. Run `01` again. What happens to the log, and why?
