"""Scorers: turn one agent run into pass/fail checks.

Three kinds, cheapest first:
  1. answer checks     plain string rules on the final answer           (free, exact)
  2. trajectory checks rules on WHICH tools ran, in what order, with
                       what arguments                                   (free, exact)
  3. LLM-as-judge      a model grades the answer against a rubric       (costs a call, fuzzy)
"""

from pydantic import BaseModel


def tool_calls(trace: list[dict]) -> list[dict]:
    return [t for t in trace if "tool" in t]


def _args_match(actual: dict, expected: dict) -> bool:
    return all(str(actual.get(k)) == str(v) for k, v in expected.items())


def check_answer(answer: str, case: dict) -> list[str]:
    """Returns a list of failure messages (empty = pass)."""
    return [f"answer missing {s!r}" for s in case.get("answer_must_include", [])
            if s.lower() not in answer.lower()]


def check_trajectory(trace: list[dict], case: dict) -> list[str]:
    calls = tool_calls(trace)
    names = [c["tool"] for c in calls]
    fails = []

    expected = case.get("expect_tools", [])
    if case.get("order", "in_order") == "in_order":
        it = iter(names)  # expected must appear as a subsequence, in order
        if not all(e in it for e in expected):
            fails.append(f"expected tools in order {expected}, got {names}")
    elif not set(expected) <= set(names):
        fails.append(f"expected tools {expected} (any order), got {names}")

    for f in case.get("forbid_tools", []):
        if f in names:
            fails.append(f"called forbidden tool {f}")

    if "max_tool_calls" in case and len(calls) > case["max_tool_calls"]:
        fails.append(f"{len(calls)} tool calls, max {case['max_tool_calls']}")

    for tool, args in case.get("expect_args", {}).items():
        if not any(c["tool"] == tool and _args_match(c["input"], args) for c in calls):
            got = [c["input"] for c in calls if c["tool"] == tool]
            fails.append(f"{tool} never called with {args}; got {got}")

    for tool, args in case.get("forbid_args", {}).items():
        if any(c["tool"] == tool and _args_match(c["input"], args) for c in calls):
            fails.append(f"{tool} was called with forbidden args {args}")
    return fails


class Verdict(BaseModel):
    passed: bool
    reason: str


def judge(answer: str, case: dict, client, model: str) -> list[str]:
    if "judge" not in case:
        return []
    resp = client.messages.parse(
        model=model, max_tokens=1024,
        system="You grade a helpdesk assistant's reply against a rubric. Be strict: fail if any part is unmet.",
        messages=[{"role": "user", "content": f"User asked: {case['input']}\n\nAssistant replied: {answer}\n\n"
                                              f"Rubric: {case['judge']}"}],
        output_format=Verdict,
    )
    v = resp.parsed_output
    return [] if v.passed else [f"judge: {v.reason}"]
