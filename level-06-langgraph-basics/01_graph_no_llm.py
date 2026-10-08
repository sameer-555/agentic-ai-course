"""A LangGraph graph with NO model at all, so you can see that a graph is just code.

Run (no API key needed):  python level-06-langgraph-basics/01_graph_no_llm.py

The parse node here is a dumb keyword parser. In 02 we replace only that node with an LLM.
"""

from datetime import timedelta

from ops_buddy import data
from leave_graph import build_graph


def keyword_parse(state):
    msg = state["message"].lower()
    leave_type = next((t for t in ("casual", "sick", "earned") if t in msg), None)
    leave_date = data.TODAY + timedelta(days=1) if "tomorrow" in msg else None
    return {"leave_type": leave_type, "leave_date": leave_date, "log": [f"parse -> {leave_type}, {leave_date}"]}


graph = build_graph(keyword_parse)

print("THE GRAPH (paste into https://mermaid.live to see it):\n")
print(graph.get_graph().draw_mermaid())

for emp, msg in [("E1042", "casual leave tomorrow please"),
                 ("E1043", "casual leave tomorrow please"),   # Rahul has 0 casual days
                 ("E1042", "I need a day off")]:
    out = graph.invoke({"employee_id": emp, "message": msg})
    print(f"\n{emp}: {msg!r}")
    for line in out["log"]:
        print(f"   {line}")
    print(f"   REPLY: {out['reply']}")
