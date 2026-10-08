"""Ops Buddy's tools: Pydantic contracts + handlers + one safe dispatcher.

This is the finished version of what students build in Level 2.
Every handler returns a dict. Problems come back as {"error": ...} with a hint
the model can act on, never as a raised exception.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from . import data

LeaveType = Literal["casual", "sick", "earned"]


# ---------- 1. Contracts: what the model is allowed to send ----------

class CheckLeaveBalance(BaseModel):
    """Look up how many leave days an employee has left, per leave type.
    Use this before applying for leave or when the user asks about their balance."""
    employee_id: str = Field(description="Employee ID like 'E1042'. Use the ID from your instructions; never guess one.")


class ApplyLeave(BaseModel):
    """Submit a one-day leave request. It goes to the employee's manager for approval;
    it is NOT approved yet. Check the balance first."""
    employee_id: str = Field(description="Employee ID like 'E1042'.")
    leave_date: date = Field(description="The day off, as YYYY-MM-DD. Must be in the future.")
    leave_type: LeaveType = Field(description="casual, sick or earned. Ask the user if unclear.")
    reason: str = Field(default="", max_length=200, description="Optional short reason.")


class CreateTicket(BaseModel):
    """Open an IT helpdesk ticket for a problem the user describes."""
    employee_id: str = Field(description="Employee ID like 'E1042'.")
    category: Literal["hardware", "software", "access", "other"]
    summary: str = Field(min_length=5, max_length=120, description="One line describing the problem.")
    priority: Literal["low", "medium", "high"] = Field(
        default="medium", description="high only if the user cannot work at all.")


class GetTicketStatus(BaseModel):
    """Get the current status of an existing IT ticket."""
    ticket_id: str = Field(pattern=r"^IT-\d{4}$", description="Ticket ID like 'IT-3001'.")


# ---------- 2. Handlers: the real work ----------

def check_leave_balance(p: CheckLeaveBalance) -> dict:
    emp = data.EMPLOYEES.get(p.employee_id)
    if emp is None:
        return {"error": f"No employee with ID {p.employee_id}. Use the ID given in your instructions."}
    return {"employee": emp["name"], "remaining_days": emp["balance"]}


def apply_leave(p: ApplyLeave) -> dict:
    emp = data.EMPLOYEES.get(p.employee_id)
    if emp is None:
        return {"error": f"No employee with ID {p.employee_id}. Use the ID given in your instructions."}
    if p.leave_date <= data.TODAY:
        return {"error": f"{p.leave_date:%A, %d %B %Y} is not in the future. Leave must be for a future date."}
    if emp["balance"][p.leave_type] < 1:
        return {"error": f"No {p.leave_type} leave left. Remaining: {emp['balance']}. "
                         "Ask the user which type to use instead; don't choose for them."}
    emp["balance"][p.leave_type] -= 1
    request_id = f"LR-{5531 + len(data.LEAVE_REQUESTS)}"
    data.LEAVE_REQUESTS[request_id] = {"employee_id": p.employee_id, "date": p.leave_date.isoformat(),
                                       "leave_type": p.leave_type, "status": "pending_manager_approval"}
    return {"request_id": request_id, "status": "pending_manager_approval",
            "date": f"{p.leave_date:%A, %d %B %Y}", "leave_type": p.leave_type}


def create_ticket(p: CreateTicket) -> dict:
    if p.employee_id not in data.EMPLOYEES:
        return {"error": f"No employee with ID {p.employee_id}."}
    ticket_id = f"IT-{3001 + len(data.TICKETS)}"
    data.TICKETS[ticket_id] = {"employee_id": p.employee_id, "category": p.category,
                               "summary": p.summary, "status": "open", "priority": p.priority}
    return {"ticket_id": ticket_id, "status": "open", "priority": p.priority}


def get_ticket_status(p: GetTicketStatus) -> dict:
    t = data.TICKETS.get(p.ticket_id)
    if t is None:
        return {"error": f"No ticket {p.ticket_id}. Ask the user to check the ID."}
    return {"ticket_id": p.ticket_id, "status": t["status"], "summary": t["summary"]}


# ---------- 3. Registry + dispatcher ----------

TOOL_MODELS = {
    "check_leave_balance": CheckLeaveBalance,
    "apply_leave": ApplyLeave,
    "create_ticket": CreateTicket,
    "get_ticket_status": GetTicketStatus,
}
HANDLERS = {
    "check_leave_balance": check_leave_balance,
    "apply_leave": apply_leave,
    "create_ticket": create_ticket,
    "get_ticket_status": get_ticket_status,
}


def tool_schema(name: str) -> dict:
    """Turn a Pydantic model into the tool format the Anthropic API expects."""
    model = TOOL_MODELS[name]
    schema = model.model_json_schema()
    schema.pop("title", None)
    schema.pop("description", None)
    return {"name": name, "description": " ".join(model.__doc__.split()), "input_schema": schema}


TOOLS = [tool_schema(n) for n in TOOL_MODELS]


def run_tool(name: str, args: dict) -> dict:
    """Validate the model's arguments, then call the handler. Never raises for bad input."""
    model = TOOL_MODELS.get(name)
    if model is None:
        return {"error": f"Unknown tool '{name}'. Available tools: {', '.join(TOOL_MODELS)}."}
    try:
        params = model.model_validate(args)
    except ValidationError as e:
        problems = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()]
        return {"error": "Invalid arguments.", "problems": problems,
                "hint": "Fix these fields and call the tool again."}
    return HANDLERS[name](params)
