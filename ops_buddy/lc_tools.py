"""The same Ops Buddy tools, wrapped for LangChain / LangGraph (Level 5 onwards).

The @tool decorator reads the function name, docstring and type hints to build
the schema, which is what Level 2 did by hand with Pydantic.
"""

from datetime import date

from langchain.tools import tool

from . import tools as t


@tool
def check_leave_balance(employee_id: str) -> dict:
    """Look up how many leave days an employee has left, per leave type.
    Use this before applying for leave or when the user asks about their balance.

    Args:
        employee_id: Employee ID like 'E1042'. Use the ID from your instructions; never guess one.
    """
    return t.run_tool("check_leave_balance", {"employee_id": employee_id})


@tool
def apply_leave(employee_id: str, leave_date: date, leave_type: t.LeaveType, reason: str = "") -> dict:
    """Submit a one-day leave request. It goes to the employee's manager for approval;
    it is NOT approved yet. Check the balance first.

    Args:
        employee_id: Employee ID like 'E1042'.
        leave_date: The day off, as YYYY-MM-DD. Must be in the future.
        leave_type: casual, sick or earned. Ask the user if unclear.
        reason: Optional short reason.
    """
    return t.run_tool("apply_leave", {"employee_id": employee_id, "leave_date": leave_date,
                                      "leave_type": leave_type, "reason": reason})


@tool
def create_ticket(employee_id: str, category: str, summary: str, priority: str = "medium") -> dict:
    """Open an IT helpdesk ticket for a problem the user describes.

    Args:
        employee_id: Employee ID like 'E1042'.
        category: One of hardware, software, access, other.
        summary: One line describing the problem.
        priority: low, medium or high. high only if the user cannot work at all.
    """
    return t.run_tool("create_ticket", {"employee_id": employee_id, "category": category,
                                        "summary": summary, "priority": priority})


@tool
def get_ticket_status(ticket_id: str) -> dict:
    """Get the current status of an existing IT ticket.

    Args:
        ticket_id: Ticket ID like 'IT-3001'.
    """
    return t.run_tool("get_ticket_status", {"ticket_id": ticket_id})


ALL_TOOLS = [check_leave_balance, apply_leave, create_ticket, get_ticket_status]
HR_TOOLS = [check_leave_balance, apply_leave]
IT_TOOLS = [create_ticket, get_ticket_status]
