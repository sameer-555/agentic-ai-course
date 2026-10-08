"""Human approval inside a create_agent agent, with HumanInTheLoopMiddleware.

Run:  python level-07-langgraph-runtime/04_approval_middleware.py
(It will ask YOU, in the terminal, to approve or reject the leave.)

Read-only tools run freely. apply_leave pauses the agent until a human decides.
"""

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from ops_buddy.config import chat_model
from ops_buddy.lc_tools import ALL_TOOLS

agent = create_agent(
    model=chat_model(),
    tools=ALL_TOOLS,
    system_prompt="You are Ops Buddy. The user's employee ID is E1042. Today is Monday, 5 October 2026.",
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"apply_leave": True,          # needs approval
                                                       "check_leave_balance": False})],
    checkpointer=InMemorySaver(),  # required: the paused run must be saved somewhere
)
config = {"configurable": {"thread_id": "chat-1"}}

result = agent.invoke({"messages": [{"role": "user", "content": "Book casual leave for this Friday."}]}, config)

while "__interrupt__" in result:
    request = result["__interrupt__"][0].value
    decisions = []
    for action in request["action_requests"]:
        print(f"\nAgent wants to run: {action['name']}({action['args']})")
        if input("Approve? [y/n] ").strip().lower() == "y":
            decisions.append({"type": "approve"})
        else:
            decisions.append({"type": "reject", "message": input("Reason: ")})
    result = agent.invoke(Command(resume={"decisions": decisions}), config)

print("\nOPS BUDDY:", result["messages"][-1].text)
