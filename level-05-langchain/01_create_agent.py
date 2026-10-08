"""Level 3's 60-line loop, rebuilt with LangChain 1.0's create_agent.

Run:  python level-05-langchain/01_create_agent.py

create_agent runs the same loop you wrote by hand: model → tools → model → ... → answer.
The tools are the same functions, wrapped with @tool (see ops_buddy/lc_tools.py).
"""

from langchain.agents import create_agent

from ops_buddy.config import chat_model
from ops_buddy.lc_tools import ALL_TOOLS

agent = create_agent(
    model=chat_model(),
    tools=ALL_TOOLS,
    system_prompt=("You are Ops Buddy, the internal helpdesk assistant. The user's employee ID is E1042. "
                   "Today is Monday, 5 October 2026. Use tools; never guess balances, dates or IDs."),
)

result = agent.invoke({"messages": [{"role": "user", "content": "Take this Friday off as casual leave."}]})

# The result is the full message list: the same thing your hand-written loop built.
for msg in result["messages"]:
    msg.pretty_print()
