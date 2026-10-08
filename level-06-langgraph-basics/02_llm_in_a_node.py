"""Same graph, but the parse node now uses an LLM with structured output.

Run:  python level-06-langgraph-basics/02_llm_in_a_node.py

Only ONE node changed. The branches, the balance check and the submission are still
plain code, so they are predictable and testable. The model does only the fuzzy part.
"""

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

from ops_buddy.config import chat_model
from leave_graph import build_graph


class Parsed(BaseModel):
    leave_date: Optional[date] = Field(description="The day off, or null if not stated.")
    leave_type: Optional[Literal["casual", "sick", "earned"]] = Field(description="null if unclear.")


parser = chat_model().with_structured_output(Parsed)


def llm_parse(state):
    p = parser.invoke(f"Today is Monday, 5 October 2026. Extract the leave request. Never guess.\n\n{state['message']}")
    return {"leave_date": p.leave_date, "leave_type": p.leave_type, "log": [f"parse (LLM) -> {p}"]}


graph = build_graph(llm_parse)

for msg in ["I've got a terrible migraine, can't come in tomorrow",
            "Want to take Friday off for my sister's engagement, use my earned leave",
            "Need some time off soon"]:
    out = graph.invoke({"employee_id": "E1042", "message": msg})
    print(f"\nUSER: {msg}")
    for line in out["log"]:
        print(f"   {line}")
    print(f"   REPLY: {out['reply']}")
