"""The agent loop, written by hand (finished version of Level 3).

Later levels reuse run_agent(): Level 12 scores its trace, Level 13 attacks it,
Level 14 serves it behind an API.
"""

import json
from collections import Counter

from . import data
from .config import MODEL, anthropic_client
from .tools import TOOLS, run_tool

MAX_STEPS = 8
MAX_INPUT_TOKENS = 50_000  # per run; tune for your model and budget

SYSTEM = """You are Ops Buddy, the company's internal helpdesk assistant.
The user's employee ID is {employee_id}. Today is {today}.
Use tools to look things up or take actions. Never guess balances, dates or IDs.
If a tool returns an error, fix your call or ask the user.
Only say an action is done if a tool result confirms it."""

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = anthropic_client()
    return _client


def run_agent(user_text, employee_id="E1042", tools=TOOLS, tool_runner=run_tool,
              system=SYSTEM, max_steps=MAX_STEPS):
    """Run one request to completion. Returns (answer, trace)."""
    client = _get_client()
    system = system.format(employee_id=employee_id, today=f"{data.TODAY:%A, %d %B %Y}")
    messages = [{"role": "user", "content": user_text}]
    trace, calls = [], Counter()
    used = {"input": 0, "output": 0}

    for step in range(1, max_steps + 1):
        # 1. DECIDE: send the whole conversation plus the tool list
        resp = client.messages.create(model=MODEL, max_tokens=4096, system=system,
                                      tools=tools, messages=messages)
        used["input"] += resp.usage.input_tokens
        used["output"] += resp.usage.output_tokens
        messages.append({"role": "assistant", "content": resp.content})

        # No tool requested: this is the final answer
        if resp.stop_reason != "tool_use":
            answer = "".join(b.text for b in resp.content if b.type == "text")
            trace.append({"step": step, "final": answer, "tokens": dict(used)})
            return answer, trace

        if used["input"] > MAX_INPUT_TOKENS:
            trace.append({"step": step, "stopped": "token budget"})
            return "This is taking longer than expected, so I've passed it to the HR team.", trace

        # 2. ACT: run every tool the model asked for in this turn
        results = []
        for block in resp.content:
            print("block============", block)
            if block.type != "tool_use":
                continue
            key = (block.name, json.dumps(block.input, sort_keys=True))
            calls[key] += 1
            if calls[key] > 2:
                output = {"error": "You've already made this exact call twice. "
                                   "Don't retry it; explain the problem to the user."}
            else:
                try:
                    output = tool_runner(block.name, block.input)
                except Exception as e:  # a bug in a tool must not kill the agent
                    output = {"error": f"The tool failed unexpectedly ({type(e).__name__}). "
                                       "Tell the user to try again later."}
            trace.append({"step": step, "tool": block.name, "input": block.input, "output": output})
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": json.dumps(output), "is_error": "error" in output})
        # print("results============================",results)
        print("token count:=======", used)
        # 3. OBSERVE: all results go back in ONE user message
        messages.append({"role": "user", "content": results})

    trace.append({"step": max_steps, "stopped": "step limit"})
    return "Sorry, I couldn't finish that. I've passed it to the HR team.", trace


def print_trace(trace):
    for t in trace:
        if "tool" in t:
            print(f"  step {t['step']}: {t['tool']}({json.dumps(t['input'])}) -> {json.dumps(t['output'])}")
        elif "final" in t:
            print(f"  step {t['step']}: FINAL  (tokens: {t['tokens']})")
        else:
            print(f"  step {t['step']}: STOPPED ({t['stopped']})")
