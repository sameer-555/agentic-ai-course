"""Pattern B: HANDOFF. A triage step passes the whole conversation to one specialist,
who then talks to the user directly.

Run:  python level-11-multi-agent/02_handoffs.py

    START → triage ─┬─▶ hr_agent ─▶ END
                    └─▶ it_agent ─▶ END

Supervisor (01): front desk stays in control and summarises.  More calls, one voice.
Handoff (02):    the specialist owns the reply.               Fewer calls, less control.
"""

from typing import Literal

from langgraph.graph import START, MessagesState, StateGraph
from langgraph.types import Command
from pydantic import BaseModel

from ops_buddy.config import chat_model
from specialists import hr_agent, it_agent


class Route(BaseModel):
    to: Literal["hr_agent", "it_agent"]


router = chat_model().with_structured_output(Route)


def triage(state: MessagesState) -> Command[Literal["hr_agent", "it_agent"]]:
    route = router.invoke([{"role": "system", "content": "Pick the specialist for this helpdesk message."},
                           *state["messages"]])
    print(f"  [triage] handing off to {route.to}")
    return Command(goto=route.to)  # the next node gets the full message history


g = StateGraph(MessagesState)
g.add_node("triage", triage)
g.add_node("hr_agent", hr_agent)   # a whole create_agent graph used as a single node
g.add_node("it_agent", it_agent)
g.add_edge(START, "triage")
graph = g.compile()

for msg in ["Do I need a medical certificate for 3 sick days?",
            "Can you check on ticket IT-3001? My battery is still dying."]:
    print(f"\nUSER: {msg}")
    out = graph.invoke({"messages": [{"role": "user", "content": msg}]})
    print(f"SPECIALIST: {out['messages'][-1].text}")
