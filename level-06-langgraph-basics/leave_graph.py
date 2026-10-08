"""The leave-request process as an explicit LangGraph graph.

    START → parse → check_balance ─┬─ enough ──────▶ submit ──┐
                                   ├─ none left ───▶ reject ──┼─▶ reply → END
                                   └─ missing info ▶ ask_user ┘

State:  a TypedDict every node reads from and returns updates to.
Nodes:  plain Python functions  state -> partial update.
Edges:  fixed (add_edge) or decided by a function (add_conditional_edges).
"""

import operator
from datetime import date
from typing import Annotated, Literal, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from ops_buddy.tools import run_tool


class LeaveState(TypedDict, total=False):
    employee_id: str
    message: str
    leave_date: Optional[date]
    leave_type: Optional[Literal["casual", "sick", "earned"]]
    balance: dict
    result: dict
    reply: str
    log: Annotated[list[str], operator.add]  # REDUCER: each node's list is appended, not overwritten


def check_balance(state: LeaveState) -> dict:
    out = run_tool("check_leave_balance", {"employee_id": state["employee_id"]})
    return {"balance": out.get("remaining_days", {}), "log": [f"check_balance -> {out}"]}


def route_after_balance(state: LeaveState) -> str:
    if not state.get("leave_date") or not state.get("leave_type"):
        return "ask_user"
    if state["balance"].get(state["leave_type"], 0) < 1:
        return "reject"
    return "submit"


def submit(state: LeaveState) -> dict:
    out = run_tool("apply_leave", {"employee_id": state["employee_id"],
                                   "leave_date": state["leave_date"], "leave_type": state["leave_type"]})
    return {"result": out, "log": [f"submit -> {out}"]}


def reject(state: LeaveState) -> dict:
    return {"result": {"error": f"you have no {state['leave_type']} leave left", "balance": state["balance"]},
            "log": ["reject"]}


def ask_user(state: LeaveState) -> dict:
    missing = [f for f in ("leave_date", "leave_type") if not state.get(f)]
    return {"result": {"need": missing}, "log": [f"ask_user (missing {missing})"]}


def reply(state: LeaveState) -> dict:
    r = state["result"]
    if "request_id" in r:
        text = f"Submitted {r['request_id']} for {r['date']} ({r['leave_type']}). Waiting for your manager."
    elif "need" in r:
        text = f"Happy to help! Please tell me the {' and '.join(x.replace('_', ' ') for x in r['need'])}."
    else:
        text = f"Sorry, {r['error']}. Your balance: {r.get('balance')}. Want to use another type?"
    return {"reply": text, "log": ["reply"]}


def build_graph(parse_node):
    """parse_node turns state['message'] into leave_date / leave_type. Level 6 swaps it for an LLM."""
    g = StateGraph(LeaveState)
    g.add_node("parse", parse_node)
    g.add_node("check_balance", check_balance)
    g.add_node("submit", submit)
    g.add_node("reject", reject)
    g.add_node("ask_user", ask_user)
    g.add_node("reply", reply)

    g.add_edge(START, "parse")
    g.add_edge("parse", "check_balance")
    g.add_conditional_edges("check_balance", route_after_balance, ["submit", "reject", "ask_user"])
    for n in ("submit", "reject", "ask_user"):
        g.add_edge(n, "reply")
    g.add_edge("reply", END)
    return g.compile()
