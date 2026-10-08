"""The whole agent loop in about 60 lines of plain Python. No framework.

Run:  python level-03-agent-by-hand/agent.py

Watch the messages list grow: user → assistant(tool_use) → user(tool_result) → ... → final.
(The same loop, with extra guard rails, lives in ops_buddy/agent.py for later levels.)
"""

import json

from ops_buddy.config import MODEL, anthropic_client
from ops_buddy.tools import TOOLS, run_tool

client = anthropic_client()
MAX_STEPS = 8

SYSTEM = """You are Ops Buddy, the company's internal helpdesk assistant.
The user's employee ID is E1042. Today is Monday, 5 October 2026.
Use tools to look things up or take actions. Never guess balances, dates or IDs.
If a tool returns an error, fix your call or ask the user.
Only say an action is done if a tool result confirms it."""


def run_agent(user_text: str, verbose: bool = True) -> str:
    messages = [{"role": "user", "content": user_text}]

    for step in range(1, MAX_STEPS + 1):
        # 1. DECIDE: the model sees the whole conversation and the tool list
        resp = client.messages.create(model=MODEL, max_tokens=4096, system=SYSTEM,
                                      tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})

        # No tool requested → this is the final answer. STOP.
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        # 2. ACT: run every tool the model asked for (it may ask for several at once)
        results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            try:
                output = run_tool(block.name, block.input)
            except Exception as e:  # a bug in a tool must not kill the agent
                output = {"error": f"Tool crashed ({type(e).__name__}). Tell the user to try later."}
            if verbose:
                print(f"  step {step}: {block.name}({json.dumps(block.input)}) -> {json.dumps(output)}")
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": json.dumps(output), "is_error": "error" in output})

        # 3. OBSERVE: all results go back in ONE user message, then loop
        messages.append({"role": "user", "content": results})

    return "Sorry, I couldn't finish that. I've passed it to the HR team."  # step limit hit


if __name__ == "__main__":
    for q in ["How many leaves do I have left?",
              "Take this Friday off as casual leave, please.",
              "My laptop screen is flickering and I can't work. Raise a ticket."]:
        print(f"\nUSER: {q}")
        print(f"OPS BUDDY: {run_agent(q)}")
