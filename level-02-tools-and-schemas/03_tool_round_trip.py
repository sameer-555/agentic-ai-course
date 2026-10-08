"""One full tool round trip, step by step, with no loop yet.

Run:  python level-02-tools-and-schemas/03_tool_round_trip.py

  1. We send the question + tool list
  2. The model replies with a tool_use block (it does NOT run the tool)
  3. WE run the tool and send back a tool_result
  4. The model writes the final answer
"""

import json

from ops_buddy.config import MODEL, anthropic_client
from ops_buddy.tools import TOOLS, run_tool

client = anthropic_client()
system = "You are Ops Buddy. The user's employee ID is E1042. Use tools; never guess numbers."
messages = [{"role": "user", "content": "How many sick days do I have left?"}]

# --- 1 + 2: the model asks for a tool
resp = client.messages.create(model=MODEL, max_tokens=2048, system=system, tools=TOOLS, messages=messages)
print("stop_reason:", resp.stop_reason)
tool_use = next(b for b in resp.content if b.type == "tool_use")
print(f"model asked for: {tool_use.name}({json.dumps(tool_use.input)})  id={tool_use.id}")

# --- 3: we run it and send the result back, matched by tool_use_id
output = run_tool(tool_use.name, tool_use.input)
print("tool returned:", output)
messages.append({"role": "assistant", "content": resp.content})
messages.append({"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": tool_use.id, "content": json.dumps(output)}
]})

# --- 4: the model answers using the result
final = client.messages.create(model=MODEL, max_tokens=2048, system=system, tools=TOOLS, messages=messages)
print("\nOPS BUDDY:", "".join(b.text for b in final.content if b.type == "text"))
