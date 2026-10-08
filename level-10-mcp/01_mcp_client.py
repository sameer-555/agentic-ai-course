"""Talk to an MCP server by hand: start it, list its tools, call one. No LLM involved.

Run (no API key needed):  python level-10-mcp/01_mcp_client.py

This is exactly what an agent framework does under the hood before giving the
tools to the model: discover → describe → call.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).parent / "leave_server.py"


async def main():
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("TOOLS the server offers:")
            for tool in (await session.list_tools()).tools:
                print(f"  - {tool.name}: {tool.description}")
                print(f"    input schema: {list(tool.inputSchema['properties'])}")

            print("\nRESOURCES:")
            for res in (await session.list_resources()).resources:
                print(f"  - {res.uri}")

            print("\nCALL check_leave_balance(E1042):")
            result = await session.call_tool("check_leave_balance", {"employee_id": "E1042"})
            print(" ", result.content[0].text)


asyncio.run(main())
