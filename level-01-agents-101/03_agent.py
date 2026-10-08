"""Way 3: an AGENT. The model decides which tool to call next, in a loop.

Run:  python level-01-agents-101/03_agent.py

This is a preview: you'll build this loop yourself in Level 3
(ops_buddy/agent.py). For now, just watch the trace: who chose each step?
"""

from ops_buddy.agent import print_trace, run_agent

for msg in ["take casual leave for this friday."]:
    print(f"\nUSER: {msg}")
    answer, trace = run_agent(msg)
    print_trace(trace)
    print(f"OPS BUDDY: {answer}")

print("\n--> Same model, but now it picks the tools and the order. That is the agent loop: model + tools + loop.")
