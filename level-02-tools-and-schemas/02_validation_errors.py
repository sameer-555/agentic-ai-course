"""What happens when the model sends bad arguments? Validate, and reply with a fixable error.

Run (no API key needed):  python level-02-tools-and-schemas/02_validation_errors.py

The model WILL sometimes send wrong types, invented IDs or past dates.
run_tool() never crashes: it returns an error the model can read and fix.
"""

import json

from ops_buddy.tools import run_tool

CASES = [
    ("good call",          "check_leave_balance", {"employee_id": "E1042"}),
    ("invented employee",  "check_leave_balance", {"employee_id": "E9999"}),
    ("missing field",      "apply_leave", {"employee_id": "E1042", "leave_type": "casual"}),
    ("wrong enum",         "apply_leave", {"employee_id": "E1042", "leave_date": "2026-10-09", "leave_type": "vacation"}),
    ("date in the past",   "apply_leave", {"employee_id": "E1042", "leave_date": "2026-09-01", "leave_type": "casual"}),
    ("no balance left",    "apply_leave", {"employee_id": "E1043", "leave_date": "2026-10-09", "leave_type": "casual"}),
    ("tool doesn't exist", "approve_my_leave", {"employee_id": "E1042"}),
    ("bad ticket id",      "get_ticket_status", {"ticket_id": "3001"}),
]

for label, name, args in CASES:
    print(f"\n# {label}\n  call:   {name}({json.dumps(args)})")
    print(f"  result: {json.dumps(run_tool(name, args), indent=None)}")

print("\n--> Each error says what went wrong AND what to do next. That is what lets the agent self-correct.")
