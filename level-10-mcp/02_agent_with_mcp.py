"""An agent whose tools ALL come from MCP servers. Zero tool code in this file.

Run:  python level-10-mcp/02_agent_with_mcp.py

MultiServerMCPClient starts both servers, asks each for its tools, and converts
them into LangChain tools. Add a third server and the agent gets its tools too.
"""

import asyncio
import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from ops_buddy.config import chat_model

HERE = Path(__file__).parent


async def main():
    client = MultiServerMCPClient({
        "leave": {"command": sys.executable, "args": [str(HERE / "leave_server.py")], "transport": "stdio"},
        "helpdesk": {"command": sys.executable, "args": [str(HERE / "helpdesk_server.py")], "transport": "stdio"},
    })
    tools = await client.get_tools()
    print("Tools discovered over MCP:", [t.name for t in tools])

    agent = create_agent(
        model=chat_model(),
        tools=tools,
        system_prompt=("You are Ops Buddy. The user is employee E1042 on the Payments team. "
                       "Today is Monday, 5 October 2026."),
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content":
        "I want to take a casual leave day this week. Which day is safe given my team's calendar? "
        "Pick the best one and apply."}]})
    print("\nOPS BUDDY:", result["messages"][-1].text)


asyncio.run(main())
