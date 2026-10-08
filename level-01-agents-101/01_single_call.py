"""Way 1: a single LLM call. No tools, no loop.

Run:  python level-01-agents-101/01_single_call.py

Predict first: the employee asks for their leave balance. What will the model say?
It has no way to look anything up, so it can only refuse or make a number up.
"""

from ops_buddy.config import MODEL, anthropic_client

client = anthropic_client()

resp = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    system="You are Ops Buddy, the company's internal helpdesk assistant.",
    messages=[{"role": "user", "content": "How many casual leaves do I have left?"}],
)

print("".join(b.text for b in resp.content if b.type == "text"))
print("\n--> No tools: the model cannot see the HR database. That is why we need tools (Level 2).")
