"""Way 2: a WORKFLOW. Your code decides every step; the model fills in the blanks.

Run:  python level-01-agents-101/02_workflow.py

Steps (fixed in code, always the same order):
  1. LLM classifies the message into a known intent   (structured output)
  2. CODE calls the right function for that intent      (no model choice)
  3. LLM writes a friendly reply from the result
"""

from typing import Literal

from pydantic import BaseModel

from ops_buddy.config import MODEL, anthropic_client
from ops_buddy.tools import CheckLeaveBalance, check_leave_balance

client = anthropic_client()
EMPLOYEE_ID = "E1042"


class Intent(BaseModel):
    intent: Literal["leave_balance", "it_problem", "other"]


def classify(message: str) -> str:
    resp = client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": f"Classify this helpdesk message:\n\n{message}"}],
        output_format=Intent,
    )
    return resp.parsed_output.intent


def reply(message: str, facts: dict) -> str:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="You are Ops Buddy. Answer in 1-2 friendly sentences using ONLY the facts given.",
        messages=[{"role": "user", "content": f"Question: {message}\nFacts: {facts}"}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def handle(message: str) -> str:
    intent = classify(message)                     # step 1: model
    print(f"  [workflow] intent = {intent}")
    if intent == "leave_balance":                  # step 2: code decides
        facts = check_leave_balance(CheckLeaveBalance(employee_id=EMPLOYEE_ID))
    elif intent == "it_problem":
        return "Please open a ticket at helpdesk.internal (Ops Buddy can't file tickets yet)."
    else:
        return "Sorry, I can only help with leave balances right now."
    return reply(message, facts)                   # step 3: model


if __name__ == "__main__":
    for msg in ["How many casual leaves do I have left?",
                "My laptop won't turn on",
                "Can I take Friday off and also check my sick leave?"]:
        print(f"\nUSER: {msg}")
        print(f"OPS BUDDY: {handle(msg)}")
    print("\n--> The last message needs two things in one go. A fixed workflow can't adapt; an agent can.")
