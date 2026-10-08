"""A tiny fake company database. Tools read and update it; reset() restores it."""

import copy
from datetime import date

TODAY = date(2026, 10, 5)  # a Monday; fixed so every run (and every eval) behaves the same

_EMPLOYEES = {
    "E1042": {"name": "Priya Sharma", "team": "Payments", "manager_id": "E2001",
              "balance": {"casual": 4, "sick": 6, "earned": 12}},
    "E1043": {"name": "Rahul Verma", "team": "Payments", "manager_id": "E2001",
              "balance": {"casual": 0, "sick": 2, "earned": 3}},
    "E1077": {"name": "Ananya Iyer", "team": "Platform", "manager_id": "E2002",
              "balance": {"casual": 7, "sick": 8, "earned": 15}},
    "E2001": {"name": "Vikram Rao", "team": "Payments", "manager_id": None,
              "balance": {"casual": 5, "sick": 8, "earned": 20}},
    "E2002": {"name": "Meera Nair", "team": "Platform", "manager_id": None,
              "balance": {"casual": 6, "sick": 8, "earned": 18}},
}

_TICKETS = {
    "IT-3001": {"employee_id": "E1077", "category": "hardware",
                "summary": "Laptop battery drains in an hour", "status": "in_progress"},
}

EMPLOYEES: dict = {}
TICKETS: dict = {}
LEAVE_REQUESTS: dict = {}


def reset():
    """Restore the starting data. Evals call this before every case."""
    EMPLOYEES.clear()
    EMPLOYEES.update(copy.deepcopy(_EMPLOYEES))
    TICKETS.clear()
    TICKETS.update(copy.deepcopy(_TICKETS))
    LEAVE_REQUESTS.clear()


reset()
