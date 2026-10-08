"""Bad tool vs good tool: the model only sees the name, description and schema.

Run (no API key needed):  python level-02-tools-and-schemas/01_bad_vs_good_tool.py

Read both as if you were the model. Which one tells you:
  - when to use it?   - what each argument means?   - which values are allowed?
"""

import json

from ops_buddy.tools import tool_schema

BAD_TOOL = {
    "name": "leave",
    "description": "leave function",
    "input_schema": {
        "type": "object",
        "properties": {"id": {"type": "string"}, "d": {"type": "string"}, "t": {"type": "string"}},
    },
}

GOOD_TOOL = tool_schema("apply_leave")  # generated from the ApplyLeave Pydantic model

print("BAD TOOL")
print(json.dumps(BAD_TOOL, indent=2))
print("\nGOOD TOOL (generated from Pydantic in ops_buddy/tools.py)")
print(json.dumps(GOOD_TOOL, indent=2))

print("""
What the good one fixes:
  name         apply_leave (verb + noun) instead of 'leave'
  description  says WHEN to use it and that the leave is NOT approved yet
  arguments    readable names, a date format, an enum for leave_type
  required     the model knows which fields it must send
""")
