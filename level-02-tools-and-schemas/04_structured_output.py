"""Structured output: get validated data back, without a tool.

Run:  python level-02-tools-and-schemas/04_structured_output.py

Tool or structured output?
  - Tool:              the model asks YOUR CODE to do something (look up, change data)
  - Structured output: you just want the model's answer in a fixed shape
"""

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

from ops_buddy.config import MODEL, anthropic_client

client = anthropic_client()


class LeaveRequest(BaseModel):
    leave_date: Optional[date] = Field(description="The day off. null if the message doesn't say.")
    leave_type: Optional[Literal["casual", "sick", "earned"]] = Field(description="null if unclear.")
    reason: str
    missing_info: list[str] = Field(description="What we still need to ask the user.")


EMAILS = [
    "Hi, I have a fever since last night, need sick leave tomorrow. Thanks, Priya",
    "Can I take a day off next week for my cousin's wedding?",
]

for email in EMAILS:
    resp = client.messages.parse(
        model=MODEL,
        max_tokens=2048,
        system="Today is Monday, 5 October 2026. Extract the leave request. Never invent a date.",
        messages=[{"role": "user", "content": email}],
        output_format=LeaveRequest,
    )
    req: LeaveRequest = resp.parsed_output  # already a validated Pydantic object
    print(f"\nEMAIL: {email}\n  -> {req.model_dump()}")
