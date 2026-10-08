"""The two specialist agents. Each has ONLY its own tools and its own instructions."""

from langchain.agents import create_agent
from langchain.tools import tool

from ops_buddy import policies
from ops_buddy.config import chat_model
from ops_buddy.lc_tools import HR_TOOLS, IT_TOOLS

CONTEXT = "The user is employee E1042 (Payments team). Today is Monday, 5 October 2026."


@tool
def search_policies(query: str) -> list[dict]:
    """Search company HR and IT policies. Returns matching sections with their source."""
    return [{"source": h["source"], "text": h["text"]} for h in policies.search(query, k=3)]


hr_agent = create_agent(
    model=chat_model(),
    tools=[*HR_TOOLS, search_policies],
    system_prompt=f"You are the HR specialist. Handle leave and HR policy only. Cite policies. {CONTEXT}",
    name="hr_agent",
)

it_agent = create_agent(
    model=chat_model(),
    tools=[*IT_TOOLS, search_policies],
    system_prompt=f"You are the IT specialist. Troubleshoot briefly, then raise or check tickets. {CONTEXT}",
    name="it_agent",
)
