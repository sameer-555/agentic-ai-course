"""Durable state: pause in one process, resume in ANOTHER, using a SQLite checkpointer.

Run (no API key needed), as three separate commands:
    python level-07-langgraph-runtime/02_survive_restart.py request Priya 2026-10-09
    python level-07-langgraph-runtime/02_survive_restart.py pending
    python level-07-langgraph-runtime/02_survive_restart.py approve <thread_id>     (or: reject <thread_id>)

Between the commands the Python process exits completely, as it would if the
server restarted. The paused run lives in approvals.sqlite, not in memory.
"""

import sys
import uuid
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

DB = "approvals.sqlite"


class State(TypedDict, total=False):
    employee: str
    leave_date: str
    approved: bool


def manager_review(state: State) -> dict:
    answer = interrupt(f"Approve leave for {state['employee']} on {state['leave_date']}?")
    return {"approved": answer == "approve"}


def finalize(state: State) -> dict:
    print(f"Leave for {state['employee']} on {state['leave_date']}: "
          f"{'APPROVED' if state['approved'] else 'REJECTED'}")
    return {}


def build(checkpointer):
    g = StateGraph(State)
    g.add_node("manager_review", manager_review)
    g.add_node("finalize", finalize)
    g.add_edge(START, "manager_review")
    g.add_edge("manager_review", "finalize")
    g.add_edge("finalize", END)
    return g.compile(checkpointer=checkpointer)


def main(cmd, *args):
    with SqliteSaver.from_conn_string(DB) as saver:
        graph = build(saver)
        if cmd == "request":
            employee, leave_date = args
            thread_id = f"leave-{uuid.uuid4().hex[:6]}"
            graph.invoke({"employee": employee, "leave_date": leave_date},
                         {"configurable": {"thread_id": thread_id}})
            print(f"Paused and saved to {DB}. thread_id = {thread_id}")
        elif cmd == "pending":
            # Collect thread IDs first: reading state while list() is still iterating deadlocks SQLite.
            thread_ids = sorted({cp.config["configurable"]["thread_id"] for cp in saver.list(None)})
            for tid in thread_ids:
                state = graph.get_state({"configurable": {"thread_id": tid}})
                if state.next:
                    print(f"{tid}: waiting at {state.next} -> {state.tasks[0].interrupts[0].value}")
        elif cmd in ("approve", "reject"):
            (thread_id,) = args
            graph.invoke(Command(resume=cmd), {"configurable": {"thread_id": thread_id}})
        else:
            print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    else:
        main(sys.argv[1], *sys.argv[2:])
