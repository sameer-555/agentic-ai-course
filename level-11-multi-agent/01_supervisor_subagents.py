"""Pattern A: SUPERVISOR with subagents as tools. The front desk stays in charge.

Run:  python level-11-multi-agent/01_supervisor_subagents.py

    user ─▶ front_desk ─┬─ ask_hr(task) ─▶ hr_agent  (own tools, own fresh context)
                        └─ ask_it(task) ─▶ it_agent
           front_desk ◀── short answers ──┘   then writes ONE reply to the user

Each subagent starts with a clean context and returns only its final answer, so
the front desk's context stays small even when the specialists do lots of work.
"""

from langchain.agents import create_agent
from langchain.tools import tool

from ops_buddy.config import chat_model
from specialists import hr_agent, it_agent


def _run(agent, task: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": task}]})
    steps = sum(1 for m in result["messages"] if m.type == "tool")
    print(f"    [{agent.name}] did {steps} tool calls for: {task!r}")
    return result["messages"][-1].text


@tool
def ask_hr(task: str) -> str:
    """Send a self-contained leave or HR-policy task to the HR specialist. Include all details it needs."""
    return _run(hr_agent, task)


@tool
def ask_it(task: str) -> str:
    """Send a self-contained IT task (tickets, laptops, access, software) to the IT specialist."""
    return _run(it_agent, task)


front_desk = create_agent(
    model=chat_model(),
    tools=[ask_hr, ask_it],
    system_prompt=("You are Ops Buddy's front desk. Split the user's message into HR and IT parts, delegate "
                   "each with ask_hr / ask_it (in parallel when possible), then reply once, briefly."),
)

msg = ("My laptop was stolen from the cafe this morning, so I need tomorrow off as casual leave "
       "to file the police report. Also, what does policy say I must do about the laptop?")
print(f"USER: {msg}\n")
result = front_desk.invoke({"messages": [{"role": "user", "content": msg}]})
print(f"\nOPS BUDDY: {result['messages'][-1].text}")
