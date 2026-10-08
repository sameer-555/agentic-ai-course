"""Pattern 2: ROUTING. Classify the input, then send it to a specialised handler.

Run:  python level-04-workflow-patterns/02_routing.py

Each route gets its own focused prompt (and later, its own tools or even a cheaper model).
Use when inputs fall into clear categories that are better handled separately.
"""

from typing import Literal

from pydantic import BaseModel

from common import ask, ask_structured


class Route(BaseModel):
    department: Literal["hr", "it", "other"]
    urgent: bool


HANDLERS = {
    "hr": "You are the HR desk. Answer about leave, payroll and policies. If you need data you don't have, say what you'd look up.",
    "it": "You are the IT desk. Give 2-3 troubleshooting steps first, then say a ticket will be raised if they don't work.",
    "other": "Politely say Ops Buddy handles HR and IT only, and suggest who might help.",
}

MESSAGES = [
    "How many sick days can I carry forward?",
    "Outlook keeps crashing when I open attachments",
    "I lost my laptop at the airport!!",
    "Where is the best biryani near the office?",
]

for msg in MESSAGES:
    route = ask_structured(f"Route this helpdesk message:\n{msg}", Route)
    reply = ask(msg, system=HANDLERS[route.department])
    flag = "  [URGENT]" if route.urgent else ""
    print(f"\nUSER: {msg}\n  -> routed to {route.department.upper()}{flag}\n  {reply[:300]}")
