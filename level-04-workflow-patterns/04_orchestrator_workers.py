"""Pattern 4: ORCHESTRATOR-WORKERS. A model plans the subtasks at run time; workers do them.

Run:  python level-04-workflow-patterns/04_orchestrator_workers.py

Unlike sectioning, the subtasks are NOT known in advance: the orchestrator decides them
from the input. Your code still owns the flow: plan → run workers → combine.
"""

from typing import Literal

from pydantic import BaseModel

from common import ask, ask_structured


class Subtask(BaseModel):
    department: Literal["hr", "it", "facilities", "finance"]
    task: str


class Plan(BaseModel):
    subtasks: list[Subtask]


WORKER_PROMPTS = {
    "hr": "You are the HR team. Describe in 1-2 lines exactly what you will do for this task.",
    "it": "You are the IT team. Describe in 1-2 lines exactly what you will set up.",
    "facilities": "You are Facilities. Describe in 1-2 lines what you will arrange.",
    "finance": "You are Finance. Describe in 1-2 lines what you will process.",
}

request = ("Ananya joins the Platform team on 19 October. She needs a laptop, GitHub and AWS access, "
           "a desk near the team, and her relocation bill from Chennai reimbursed.")

# 1. Orchestrator: break the request down (the model decides how many subtasks and which)
plan = ask_structured(f"Break this onboarding request into one subtask per department needed:\n{request}",
                      Plan, system="You are an onboarding coordinator.")
print("PLAN")
for s in plan.subtasks:
    print(f"  [{s.department}] {s.task}")

# 2. Workers: each subtask goes to a specialised prompt
outputs = [(s.department, ask(s.task, system=WORKER_PROMPTS[s.department])) for s in plan.subtasks]

# 3. Synthesiser: combine worker outputs into one answer
summary = ask("Write a short onboarding checklist for the hiring manager from these team updates:\n\n"
              + "\n".join(f"{d.upper()}: {o}" for d, o in outputs))
print("\nCHECKLIST\n" + summary)
