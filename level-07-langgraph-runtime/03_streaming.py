"""Streaming: show progress while the agent works, instead of a long silence.

Run:  python level-07-langgraph-runtime/03_streaming.py

Two stream modes at once:
  "updates"  → one event per finished step (which node ran, which tool was called)
  "messages" → the model's text token by token, as it is generated
"""

from langchain.agents import create_agent

from ops_buddy.config import chat_model
from ops_buddy.lc_tools import ALL_TOOLS

agent = create_agent(
    model=chat_model(),
    tools=ALL_TOOLS,
    system_prompt="You are Ops Buddy. The user's employee ID is E1042. Today is Monday, 5 October 2026.",
)

question = "What's my leave balance, and what's the status of ticket IT-3001?"
for mode, chunk in agent.stream({"messages": [{"role": "user", "content": question}]},
                                stream_mode=["updates", "messages"]):
    if mode == "updates":
        for node, update in chunk.items():
            for msg in (update or {}).get("messages", []):
                for call in getattr(msg, "tool_calls", []) or []:
                    print(f"\n  [step: {node}] calling {call['name']}({call['args']})")
                if msg.type == "tool":
                    print(f"  [step: {node}] result: {msg.content[:100]}")
    else:  # "messages": (token_chunk, metadata)
        token, meta = chunk
        if meta.get("langgraph_node") == "model" and token.text:
            print(token.text, end="", flush=True)
print()
