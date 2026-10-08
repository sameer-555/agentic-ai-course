"""Short-term memory = the conversation, saved per thread by a checkpointer.

Run:  python level-08-memory-and-context/01_short_term_memory.py

Same thread_id → the agent remembers earlier turns.
New thread_id  → a fresh conversation; it remembers nothing.
"""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from ops_buddy.config import chat_model
from ops_buddy.lc_tools import ALL_TOOLS

agent = create_agent(
    model=chat_model(),
    tools=ALL_TOOLS,
    system_prompt="You are Ops Buddy. The user's employee ID is E1042. Today is Monday, 5 October 2026.",
    checkpointer=InMemorySaver(),
)


def chat(thread_id: str, text: str):
    result = agent.invoke({"messages": [{"role": "user", "content": text}]},
                          {"configurable": {"thread_id": thread_id}})
    print(f"[{thread_id}] USER: {text}\n[{thread_id}] OPS BUDDY: {result['messages'][-1].text}\n")


chat("monday-chat", "How many earned leaves do I have?")
chat("monday-chat", "OK, book one of those for next Monday.")   # "those" only makes sense with memory
chat("tuesday-chat", "Book one of those for next Monday.")       # new thread: "those" means nothing
