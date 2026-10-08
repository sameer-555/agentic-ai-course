"""Ops Buddy as a web service: streaming replies, retries, token budgets and a cost cap.

Run the server:   uvicorn app:app --app-dir level-14-ship-it --port 8000
Talk to it:       python level-14-ship-it/client.py "How many sick days do I have?"
API docs:         http://localhost:8000/docs

This is the Level 3 loop again, now with what production needs around it:
  - Server-Sent Events: the user sees tool steps and text as they happen
  - SDK retries + timeouts, and friendly errors when the API is busy or down
  - A per-request token budget, and a per-employee daily cost cap
  - The secured tools from Level 13 (identity comes from the request header, not the model)
"""

import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import anthropic
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ops_buddy import data
from ops_buddy.config import MODEL

sys.path.insert(0, str(Path(__file__).parents[1] / "level-13-guardrails"))
from secure_agent import SECURE_SYSTEM, SECURE_TOOLS, make_secure_runner  # noqa: E402

MAX_STEPS = 6
MAX_INPUT_TOKENS_PER_REQUEST = 40_000
DAILY_COST_CAP_USD = 0.50                      # per employee per day
PRICE_PER_MTOK = {"input": 5.00, "output": 25.00}  # check current pricing for your model

client = anthropic.Anthropic(max_retries=3, timeout=60)  # retries 429/5xx/connection errors with backoff
app = FastAPI(title="Ops Buddy")

SESSIONS: dict[str, list] = defaultdict(list)          # use Redis/Postgres in real deployments
SPEND: dict[tuple[str, date], float] = defaultdict(float)


class ChatIn(BaseModel):
    message: str
    session_id: str = "default"


def cost_usd(usage) -> float:
    return (usage.input_tokens * PRICE_PER_MTOK["input"] + usage.output_tokens * PRICE_PER_MTOK["output"]) / 1e6


def over_budget(employee_id: str, today: date) -> bool:
    return SPEND[(employee_id, today)] >= DAILY_COST_CAP_USD


def sse(event: str, payload) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, default=str)}\n\n"


def agent_stream(employee_id: str, session_id: str, message: str):
    today = date.today()
    history = SESSIONS[f"{employee_id}:{session_id}"]
    history.append({"role": "user", "content": message})
    system = SECURE_SYSTEM.format(employee_id=employee_id, today=f"{data.TODAY:%A, %d %B %Y}")
    run_tool = make_secure_runner(employee_id)
    used_input = 0

    try:
        for _ in range(MAX_STEPS):
            with client.messages.stream(model=MODEL, max_tokens=4096, system=system,
                                        tools=SECURE_TOOLS, messages=history) as stream:
                for text in stream.text_stream:            # text arrives token by token
                    yield sse("text", text)
                msg = stream.get_final_message()

            SPEND[(employee_id, today)] += cost_usd(msg.usage)
            used_input += msg.usage.input_tokens
            history.append({"role": "assistant", "content": msg.content})

            if msg.stop_reason != "tool_use":
                yield sse("done", {"spent_today_usd": round(SPEND[(employee_id, today)], 4)})
                return
            if used_input > MAX_INPUT_TOKENS_PER_REQUEST or over_budget(employee_id, today):
                break

            results = []
            for block in msg.content:
                if block.type == "tool_use":
                    yield sse("tool", {"name": block.name, "input": block.input})
                    output = run_tool(block.name, block.input)
                    results.append({"type": "tool_result", "tool_use_id": block.id,
                                    "content": json.dumps(output, default=str), "is_error": "error" in output})
            history.append({"role": "user", "content": results})

        # Budget or step limit hit. Drop an unanswered tool request so the saved history stays valid.
        if history[-1]["role"] == "assistant":
            history.pop()
        history.append({"role": "assistant", "content": "I had to stop here and passed this to the HR team."})
        yield sse("text", "\nThis is taking longer than expected, so I've passed it to the HR team.")
        yield sse("done", {"stopped": "budget or step limit"})

    except anthropic.RateLimitError:
        yield sse("error", "Ops Buddy is very busy right now. Please try again in a minute.")
    except anthropic.APIConnectionError:
        yield sse("error", "Ops Buddy can't reach its AI service right now. Please try again shortly.")
    except anthropic.APIStatusError as e:
        yield sse("error", f"Something went wrong (code {e.status_code}). The team has been notified.")


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


@app.post("/chat")
def chat(body: ChatIn, x_employee_id: str | None = Header(default=None)):
    # In production this comes from your login system (SSO/JWT), never from a header the user can type.
    if not x_employee_id or x_employee_id not in data.EMPLOYEES:
        raise HTTPException(401, "Unknown employee. Send X-Employee-Id.")
    if over_budget(x_employee_id, date.today()):
        raise HTTPException(429, "Daily Ops Buddy budget reached. It resets tomorrow.")
    return StreamingResponse(agent_stream(x_employee_id, body.session_id, body.message),
                             media_type="text/event-stream")
