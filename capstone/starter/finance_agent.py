"""The Finance specialist agent: STARTER. Works now with list_my_claims; grows as you finish the TODOs.

Run:  python capstone/starter/finance_agent.py

To plug into Level 11's front desk, add a tool there:
    @tool
    def ask_finance(task: str) -> str:
        "Send a reimbursement or claims task to the Finance specialist."
        return _run(build_finance_agent("E1042"), task)
"""

from langchain.agents import create_agent
from langchain.tools import tool

from ops_buddy import policies
from ops_buddy.config import chat_model
from finance_tools import run_finance_tool


def build_finance_agent(employee_id: str):
    # Tools are built per user, so identity is fixed by our code and invisible to the model (Level 13).
    @tool
    def list_my_claims(status: str = "any") -> dict:
        """List the current user's reimbursement claims. status: any, pending_manager_approval, approved, paid, rejected."""
        return run_finance_tool("list_my_claims", {"status": status}, employee_id)

    @tool
    def submit_claim(type: str, amount: int, expense_date: str) -> dict:
        """Submit a reimbursement claim (medical, travel or internet). Amount in rupees, date as YYYY-MM-DD.
        Claims over Rs 10,000 go to the manager for approval."""
        return run_finance_tool("submit_claim", {"type": type, "amount": amount, "expense_date": expense_date},
                                employee_id)

    @tool
    def search_policies(query: str) -> list[dict]:
        """Search company policies (reimbursement rules, forms, limits). Returns sections with sources."""
        return [{"source": h["source"], "text": h["text"]} for h in policies.search(query, k=3)]

    return create_agent(
        model=chat_model(),
        tools=[list_my_claims, submit_claim, search_policies],
        system_prompt=("You are the Finance specialist for Ops Buddy. Handle reimbursement claims only. "
                       "Cite policies like [Reimbursement Policy > Travel claims]. Today is Monday, 5 October 2026."),
        name="finance_agent",
    )


if __name__ == "__main__":
    agent = build_finance_agent("E1042")
    for q in ["What claims do I have pending?", "How long do I have to submit a travel claim?"]:
        result = agent.invoke({"messages": [{"role": "user", "content": q}]})
        print(f"\nUSER: {q}\nFINANCE: {result['messages'][-1].text}")
