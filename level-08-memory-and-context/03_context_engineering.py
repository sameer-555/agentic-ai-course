"""Context engineering: decide exactly what the model sees at each step.

Run:  python level-08-memory-and-context/03_context_engineering.py

The context window is a budget. Long chats fill it with stale tool results, which
costs money and makes answers worse ("context rot"). Two fixes, measured with
the API's token counter:
  1. Clear old tool results  (keep the last N; replace older ones with a stub)
  2. Compact                 (summarise old turns into one short message)
"""

import copy
import json

from ops_buddy.config import MODEL, anthropic_client
from ops_buddy.tools import TOOLS

client = anthropic_client()
SYSTEM = "You are Ops Buddy. The user's employee ID is E1042."


def fake_long_chat(turns: int = 15) -> list:
    """Build a realistic chat: each turn has a tool call with a big result."""
    messages = []
    for i in range(turns):
        messages.append({"role": "user", "content": f"Question {i}: what's the status of ticket IT-{3001 + i}?"})
        messages.append({"role": "assistant", "content": [
            {"type": "tool_use", "id": f"toolu_{i:02d}", "name": "get_ticket_status",
             "input": {"ticket_id": f"IT-{3001 + i}"}}]})
        big_result = {"ticket_id": f"IT-{3001 + i}", "status": "open",
                      "history": [f"update {j}: engineer looked at logs, no change" for j in range(40)]}
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": f"toolu_{i:02d}", "content": json.dumps(big_result)}]})
        messages.append({"role": "assistant", "content": f"Ticket IT-{3001 + i} is still open."})
    messages.append({"role": "user", "content": "Which tickets did we talk about, and are any closed?"})
    return messages


def count(messages) -> int:
    return client.messages.count_tokens(model=MODEL, system=SYSTEM, tools=TOOLS,
                                        messages=messages).input_tokens


def clear_old_tool_results(messages, keep_last: int = 3):
    """Fix 1: keep the newest N tool results in full, stub out the rest."""
    messages = copy.deepcopy(messages)
    results = [b for m in messages if isinstance(m["content"], list)
               for b in m["content"] if b["type"] == "tool_result"]
    for block in results[:-keep_last]:
        block["content"] = "[old result cleared to save space]"
    return messages


def compact(messages, keep_last_turns: int = 2):
    """Fix 2: summarise everything except the last few turns into one message."""
    cut = len(messages) - 1 - keep_last_turns * 4  # 4 messages per turn in fake_long_chat
    old, recent = messages[:cut], messages[cut:]
    transcript = json.dumps(old)[:60_000]
    summary = client.messages.create(
        model=MODEL, max_tokens=1024,
        messages=[{"role": "user", "content": "Summarise this helpdesk chat in under 120 words. Keep every "
                                              f"ticket ID and its status.\n\n{transcript}"}],
    )
    text = "".join(b.text for b in summary.content if b.type == "text")
    return [{"role": "user", "content": f"(Summary of our earlier conversation: {text})"},
            {"role": "assistant", "content": "Got it."}, *recent]


chat = fake_long_chat()
print(f"{'Original chat':30s}{count(chat):>8,} tokens")
print(f"{'After clearing old results':30s}{count(clear_old_tool_results(chat)):>8,} tokens")
print(f"{'After compaction':30s}{count(compact(chat)):>8,} tokens")
print("\nThe built-in versions: SummarizationMiddleware / ContextEditingMiddleware (LangChain),"
      "\nor server-side context editing and compaction in the Claude API.")
