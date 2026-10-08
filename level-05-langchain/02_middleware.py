"""Middleware: hooks that run before/after model calls and around tool calls.

Run:  python level-05-langchain/02_middleware.py

Everything you hand-coded in Level 3's guard rails becomes a line of config:
  ModelCallLimitMiddleware   → MAX_STEPS
  SummarizationMiddleware    → keeps long chats under the context limit
  @before_model / @wrap_tool_call → your own logging, timing, checks
"""

import time

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    SummarizationMiddleware,
    before_model,
    wrap_tool_call,
)

from ops_buddy.config import chat_model
from ops_buddy.lc_tools import ALL_TOOLS


@before_model
def log_model_call(state, runtime):
    print(f"  [before_model] sending {len(state['messages'])} messages to the model")


@wrap_tool_call
def time_tool(request, handler):
    start = time.perf_counter()
    result = handler(request)  # actually runs the tool
    ms = (time.perf_counter() - start) * 1000
    print(f"  [tool] {request.tool_call['name']}({request.tool_call['args']}) took {ms:.1f} ms")
    return result


agent = create_agent(
    model=chat_model(),
    tools=ALL_TOOLS,
    system_prompt="You are Ops Buddy. The user's employee ID is E1042. Today is Monday, 5 October 2026.",
    middleware=[
        ModelCallLimitMiddleware(run_limit=6, exit_behavior="end"),         # step limit
        SummarizationMiddleware(model=chat_model(), trigger=("tokens", 4000),  # auto-summarised history
                                keep=("messages", 6)),
        log_model_call,
        time_tool,
    ],
)

result = agent.invoke({"messages": [{"role": "user", "content":
    "Check my balance, then book sick leave for tomorrow, and raise a ticket: my VPN keeps disconnecting."}]})
print("\nOPS BUDDY:", result["messages"][-1].text)
