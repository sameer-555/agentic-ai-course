"""Pattern 5: EVALUATOR-OPTIMIZER. One call writes, another grades; loop until it passes.

Run:  python level-04-workflow-patterns/05_evaluator_optimizer.py

Use when you have clear criteria and a first draft is usually not good enough.
Always cap the number of rounds.
"""

from pydantic import BaseModel

from common import ask, ask_structured

MAX_ROUNDS = 3
CRITERIA = """1. Says the leave request is SUBMITTED and waiting for the manager, never 'approved'.
2. Mentions the request ID LR-5531.
3. Mentions the remaining casual balance (3 days).
4. At most 3 sentences. No emojis."""


class Grade(BaseModel):
    passed: bool
    feedback: str


facts = "Leave request LR-5531 for Friday 9 Oct (casual) is pending manager approval. Casual balance now 3."
draft = ask(f"Write a cheerful reply to the employee using these facts: {facts}")

for round_no in range(1, MAX_ROUNDS + 1):
    grade = ask_structured(f"Criteria:\n{CRITERIA}\n\nReply to grade:\n{draft}", Grade,
                           system="You are a strict reviewer. Fail the reply if ANY criterion is not met.")
    print(f"\nROUND {round_no}\n  draft: {draft}\n  passed: {grade.passed}  feedback: {grade.feedback}")
    if grade.passed:
        break
    draft = ask(f"Rewrite this reply to fix the feedback.\nFacts: {facts}\nFeedback: {grade.feedback}\nReply: {draft}")
else:
    print("\nStill failing after max rounds: send to a human instead of looping forever.")
