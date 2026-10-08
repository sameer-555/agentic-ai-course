"""Long-term memory = facts that survive across conversations, kept in a Store.

Run:  python level-08-memory-and-context/02_long_term_memory.py

- The agent saves preferences with a tool (remember_preference).
- A dynamic prompt loads them into the system prompt at the start of EVERY conversation.
- Memories are namespaced per employee, so Priya never sees Rahul's.
In production, swap InMemoryStore for a database-backed store (e.g. Postgres).
"""

from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from ops_buddy.config import chat_model
from ops_buddy.lc_tools import ALL_TOOLS


@dataclass
class Ctx:
    employee_id: str  # set by OUR code per request, never by the model


@tool
def remember_preference(key: str, value: str, runtime: ToolRuntime) -> str:
    """Save a lasting preference or fact about the current user, e.g. key='language', value='Hindi'.
    Only save things the user would want remembered next time."""
    runtime.store.put(("employees", runtime.context.employee_id), key, {"value": value})
    return f"Saved {key} = {value}"


@dynamic_prompt
def with_memories(request) -> str:
    emp = request.runtime.context.employee_id
    items = request.runtime.store.search(("employees", emp))
    memories = "\n".join(f"- {i.key}: {i.value['value']}" for i in items) or "- (nothing yet)"
    return (f"You are Ops Buddy. The user's employee ID is {emp}. Today is Monday, 5 October 2026.\n"
            f"What you remember about this user:\n{memories}")


agent = create_agent(
    model=chat_model(),
    tools=[*ALL_TOOLS, remember_preference],
    middleware=[with_memories],
    context_schema=Ctx,
    checkpointer=InMemorySaver(),  # short-term (per thread)
    store=InMemoryStore(),         # long-term (across threads)
)


def chat(emp: str, thread: str, text: str):
    result = agent.invoke({"messages": [{"role": "user", "content": text}]},
                          {"configurable": {"thread_id": thread}}, context=Ctx(employee_id=emp))
    print(f"[{emp} / {thread}] USER: {text}\n   OPS BUDDY: {result['messages'][-1].text}\n")


chat("E1042", "week-1", "Please always reply to me in Hindi. And I prefer earned leave over casual.")
chat("E1042", "week-2", "Book a day off for this Friday.")   # new thread: does it still know?
chat("E1043", "week-2b", "What language do I prefer?")         # different employee: must not know
