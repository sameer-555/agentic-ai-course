"""Ops Buddy's leave tools, exposed as an MCP server.

Any MCP client can now use them: our own agent (02), Claude Desktop, Claude Code, an IDE...
You don't run this file directly; clients start it and talk to it over stdin/stdout.

Try it in Claude Code:   claude mcp add ops-buddy-leave -- python /full/path/to/leave_server.py
"""

from datetime import date
from typing import Literal

from mcp.server.fastmcp import FastMCP

from ops_buddy import tools as t

mcp = FastMCP("ops-buddy-leave", log_level="WARNING")


@mcp.tool()
def check_leave_balance(employee_id: str) -> dict:
    """Look up how many leave days an employee has left, per leave type."""
    return t.run_tool("check_leave_balance", {"employee_id": employee_id})


@mcp.tool()
def apply_leave(employee_id: str, leave_date: date, leave_type: Literal["casual", "sick", "earned"]) -> dict:
    """Submit a one-day leave request for manager approval (NOT approved yet). Date as YYYY-MM-DD."""
    return t.run_tool("apply_leave", {"employee_id": employee_id, "leave_date": leave_date,
                                      "leave_type": leave_type})


@mcp.resource("policy://leave")
def leave_policy() -> str:
    """The full leave policy, as a readable resource."""
    from ops_buddy.policies import POLICY_DIR
    return (POLICY_DIR / "leave-policy.md").read_text()


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
