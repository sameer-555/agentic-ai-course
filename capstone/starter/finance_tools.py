"""Finance department tools: STARTER. One tool is finished; two are TODO.

Follow the Level 2 pattern: Pydantic contract → handler → registry → run_tool.
Notice: no employee_id in the contracts. Identity comes from the session (Level 13).
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from ops_buddy import data

CLAIMS = {
    "CL-7001": {"employee_id": "E1042", "type": "medical", "amount": 4200, "status": "paid"},
    "CL-7002": {"employee_id": "E1042", "type": "travel", "amount": 18500, "status": "pending_manager_approval"},
}
APPROVAL_LIMIT = 10_000  # claims above this need a manager (Level 7 / 13)


class ListMyClaims(BaseModel):
    """List the current user's reimbursement claims with their status."""
    status: Literal["any", "pending_manager_approval", "approved", "paid", "rejected"] = "any"


def list_my_claims(p: ListMyClaims, employee_id: str) -> dict:
    mine = {cid: c for cid, c in CLAIMS.items() if c["employee_id"] == employee_id
            and (p.status == "any" or c["status"] == p.status)}
    return {"claims": mine} if mine else {"claims": {}, "note": "No claims found."}


class SubmitClaim(BaseModel):
    """Submit a reimbursement claim. Medical uses Form HR-204, travel uses Form HR-209.
    Claims over Rs 10,000 go to the manager for approval."""
    type: Literal["medical", "travel", "internet"]
    amount: int = Field(gt=0, le=100_000, description="Amount in rupees.")
    expense_date: date = Field(description="When the money was spent, YYYY-MM-DD.")


def submit_claim(p: SubmitClaim, employee_id: str) -> dict:
    # TODO 1: reject expense dates in the future (compare with data.TODAY)
    # TODO 2: reject medical claims older than 30 days and travel claims older than 15 (see reimbursement.md)
    # TODO 3: create a new CL-xxxx id, store it in CLAIMS with status
    #         "pending_manager_approval" if amount > APPROVAL_LIMIT else "approved"
    return {"error": "submit_claim is not implemented yet."}


# TODO 4: add a GetClaimStatus contract + handler. It must refuse claims that belong to someone else.


TOOL_MODELS = {"list_my_claims": ListMyClaims, "submit_claim": SubmitClaim}
HANDLERS = {"list_my_claims": list_my_claims, "submit_claim": submit_claim}


def run_finance_tool(name: str, args: dict, employee_id: str) -> dict:
    model = TOOL_MODELS.get(name)
    if model is None:
        return {"error": f"Unknown tool '{name}'. Available: {', '.join(TOOL_MODELS)}."}
    try:
        params = model.model_validate(args)
    except ValidationError as e:
        return {"error": "Invalid arguments.", "problems": [f"{'.'.join(map(str, x['loc']))}: {x['msg']}"
                                                            for x in e.errors()]}
    return HANDLERS[name](params, employee_id)


if __name__ == "__main__":
    print(run_finance_tool("list_my_claims", {}, "E1042"))
    print(run_finance_tool("submit_claim", {"type": "medical", "amount": 2500, "expense_date": str(data.TODAY)}, "E1042"))
