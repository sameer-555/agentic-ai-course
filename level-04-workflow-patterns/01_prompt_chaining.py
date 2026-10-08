"""Pattern 1: PROMPT CHAINING. Output of step N is the input of step N+1, with a check in between.

Run:  python level-04-workflow-patterns/01_prompt_chaining.py

  draft announcement → GATE (code check) → translate to Hindi
Use when a task splits cleanly into fixed steps and each step is easier than the whole.
"""

from common import ask

policy_change = "From 1 November, WFH goes from 2 to 3 days a week for employees past probation. Interns unchanged."

# Step 1: draft
draft = ask(f"Write a 3-sentence Slack announcement for employees about this change:\n{policy_change}")
print("STEP 1 - draft:\n", draft)

# Gate: plain code checks the draft before we spend another call
problems = [w for w in ["3", "november", "intern"] if w not in draft.lower()]  # loose: "1 November" or "November 1" both pass
if problems:
    print(f"\nGATE FAILED, missing: {problems}. Stopping the chain instead of translating a wrong draft.")
    raise SystemExit(1)
print("\nGATE passed: all key facts present.")

# Step 2: transform
hindi = ask(f"Translate this announcement into simple Hindi (Devanagari). Keep dates and numbers as digits:\n\n{draft}")
print("\nSTEP 2 - Hindi version:\n", hindi)
