"""Agentic RAG, step 1: retrieval is just another tool the agent CHOOSES to call.

Run:  python level-09-agentic-rag/01_retrieval_as_tool.py

Classic RAG always retrieves once, before the model runs. Here the agent decides:
  - whether it needs the policy at all ("what's my balance?" → no)
  - what to search for, and whether to search again
  - how to combine policy text with live data from the HR tools
"""

from langchain.agents import create_agent
from langchain.tools import tool

from ops_buddy import policies
from ops_buddy.config import chat_model
from ops_buddy.lc_tools import ALL_TOOLS


@tool
def search_policies(query: str) -> list[dict]:
    """Search the company HR, IT and reimbursement policies. Returns the best matching sections
    with their source. Use short keyword queries; search again with different words if the
    results don't answer the question."""
    return [{"source": h["source"], "text": h["text"]} for h in policies.search(query, k=3)]


agent = create_agent(
    model=chat_model(),
    tools=[search_policies, *ALL_TOOLS],
    system_prompt=(
        "You are Ops Buddy. The user's employee ID is E1042. Today is Monday, 5 October 2026.\n"
        "For any question about rules or policy, search the policies first. Answer only from what you find, "
        "and cite each fact like [Leave Policy > Sick leave]. If the policies don't cover it, say so."),
)

for q in ["I was sick for 3 days last week. Do I need to do anything?",
          "Can I carry my earned leave into next year, and how much do I have right now?",
          "What's the company policy on bringing pets to the office?"]:
    result = agent.invoke({"messages": [{"role": "user", "content": q}]})
    tools_used = [c["name"] for m in result["messages"] for c in (getattr(m, "tool_calls", None) or [])]
    print(f"\nUSER: {q}\n  tools used: {tools_used}\nOPS BUDDY: {result['messages'][-1].text}")
