"""YOUR TURN: finish the agent loop. Fill in the three TODOs.

Run:  python level-03-agent-by-hand/03_your_turn.py
Stuck? Compare with agent.py in this folder, but try for 15 minutes first.
"""

import json

from ops_buddy.config import MODEL, anthropic_client
from ops_buddy.tools import TOOLS, run_tool

client = anthropic_client()
SYSTEM = "You are Ops Buddy. The user's employee ID is E1042. Today is Monday, 5 October 2026. Use tools; never guess."


def run_agent(user_text: str, max_steps: int = 6) -> str:
    messages = [{"role": "user", "content": user_text}]
    for step in range(max_steps):
        resp = client.messages.create(model=MODEL, max_tokens=4096, system=SYSTEM,
                                      tools=TOOLS, messages=messages)

        # TODO 1: add the model's reply to `messages` (hint: role "assistant", content = resp.content)

        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                output = run_tool(block.name, block.input)
                # TODO 2: append a tool_result dict to `results`
                #         (keys: type, tool_use_id, content as a JSON string)
                pass

        # TODO 3: send all results back to the model in ONE user message

    return "Step limit reached."


if __name__ == "__main__":
    print(run_agent("Do I have enough sick leave to take two days off?"))
