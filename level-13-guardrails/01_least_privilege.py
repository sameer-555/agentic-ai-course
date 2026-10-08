"""Least privilege, enforced in code. No model needed to see it work.

Run (no API key needed):  python level-13-guardrails/01_least_privilege.py
"""

import json

from ops_buddy.tools import tool_schema
from secure_agent import SECURE_TOOLS, make_secure_runner

print("BEFORE: the model chooses whose records to read")
print("  check_leave_balance params:", list(tool_schema("check_leave_balance")["input_schema"]["properties"]))
print("AFTER: the parameter is gone; our code fills it in from the session")
print("  check_leave_balance params:", list(SECURE_TOOLS[0]["input_schema"]["properties"]))

runner = make_secure_runner("E1042", needs_approval={"apply_leave"}, approve=lambda name, args: False)

print("\nPriya (E1042) is logged in:")
for name, args in [
    ("check_leave_balance", {}),                                   # normal use
    ("check_leave_balance", {"employee_id": "E1043"}),             # tricked into asking for Rahul's
    ("apply_leave", {"leave_date": "2026-10-12", "leave_type": "earned"}),  # write action, no approval
]:
    print(f"  {name}({json.dumps(args)})\n     -> {json.dumps(runner(name, args))}")
