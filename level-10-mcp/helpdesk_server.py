"""A second MCP server: IT ticketing + a team calendar.

In real life this would be someone else's server (Jira, ServiceNow, Google Calendar...).
The point of MCP: Ops Buddy plugs into it without any custom integration code.
"""

from typing import Literal

from mcp.server.fastmcp import FastMCP

from ops_buddy import tools as t

mcp = FastMCP("helpdesk", log_level="WARNING")

TEAM_CALENDAR = {
    "Payments": [{"date": "2026-10-09", "event": "Release v4.2 (all hands on deck)"},
                 {"date": "2026-10-20", "event": "Diwali holiday"}],
    "Platform": [{"date": "2026-10-14", "event": "Infra migration window"},
                 {"date": "2026-10-20", "event": "Diwali holiday"}],
}


@mcp.tool()
def create_ticket(employee_id: str, category: Literal["hardware", "software", "access", "other"],
                  summary: str, priority: Literal["low", "medium", "high"] = "medium") -> dict:
    """Open an IT helpdesk ticket."""
    return t.run_tool("create_ticket", {"employee_id": employee_id, "category": category,
                                        "summary": summary, "priority": priority})


@mcp.tool()
def get_ticket_status(ticket_id: str) -> dict:
    """Get the status of an IT ticket like 'IT-3001'."""
    return t.run_tool("get_ticket_status", {"ticket_id": ticket_id})


@mcp.tool()
def team_calendar(team: Literal["Payments", "Platform"]) -> list[dict]:
    """Upcoming releases, freezes and holidays for a team. Check before suggesting leave dates."""
    return TEAM_CALENDAR[team]


if __name__ == "__main__":
    mcp.run()
