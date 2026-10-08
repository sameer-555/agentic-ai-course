"""Guard rails: what stops an agent from looping forever or crashing?

Run:  python level-03-agent-by-hand/02_guard_rails.py

We give the agent a BROKEN tool runner on purpose and watch the guard rails work:
  - a crashing tool becomes an error message, not a Python traceback
  - the same failing call is blocked after 2 tries
  - the step limit and token budget always end the run
The production-style loop is ops_buddy/agent.py; read it alongside this output.
"""

from ops_buddy.agent import print_trace, run_agent


def flaky_tool_runner(name, args):
    raise TimeoutError("HR database did not respond")  # every call fails


answer, trace = run_agent("How many casual leaves do I have?", tool_runner=flaky_tool_runner)
print_trace(trace)
print(f"\nOPS BUDDY: {answer}")
print(f"\nSteps used: {trace[-1]['step']} (limit 8). The agent stopped by itself and told the user.")
