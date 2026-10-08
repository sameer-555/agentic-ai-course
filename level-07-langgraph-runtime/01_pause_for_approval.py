"""Pause a run for a human, then resume it. Checkpointer + interrupt().

Run (no API key needed):  python level-07-langgraph-runtime/01_pause_for_approval.py

  submit ─▶ manager_review (PAUSES here) ─▶ finalize
The checkpointer saves state after every step, keyed by thread_id.
interrupt() stops the run; Command(resume=...) continues it with the human's answer.
"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict, total=False):
    employee: str
    leave_date: str
    decision: dict
    status: str


def submit(state: State) -> dict:
    print(f"  [submit] {state['employee']} asked for leave on {state['leave_date']}")
    return {"status": "pending"}


def manager_review(state: State) -> dict:
    # Everything ABOVE interrupt() runs again on resume, so keep side effects out of this node.
    decision = interrupt({"question": f"Approve leave for {state['employee']} on {state['leave_date']}?"})
    return {"decision": decision}


def finalize(state: State) -> dict:
    d = state["decision"]
    status = "approved" if d["approved"] else f"rejected ({d.get('note', 'no reason')})"
    print(f"  [finalize] leave {status}")
    return {"status": status}


g = StateGraph(State)
g.add_node("submit", submit)
g.add_node("manager_review", manager_review)
g.add_node("finalize", finalize)
g.add_edge(START, "submit")
g.add_edge("submit", "manager_review")
g.add_edge("manager_review", "finalize")
g.add_edge("finalize", END)
graph = g.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "leave-LR-5531"}}

print("RUN 1: employee submits")
result = graph.invoke({"employee": "Priya Sharma", "leave_date": "2026-10-09"}, config)
print("  paused with:", result["__interrupt__"][0].value)
print("  next node waiting:", graph.get_state(config).next)

print("\n... hours later, the manager clicks Approve ...\n")

print("RUN 2: resume the SAME thread with the manager's answer")
result = graph.invoke(Command(resume={"approved": True}), config)
print("  final status:", result["status"])
