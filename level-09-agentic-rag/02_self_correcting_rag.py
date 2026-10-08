"""Agentic RAG, step 2: retrieve → grade → (rewrite and retry) → answer with citations.

Run:  python level-09-agentic-rag/02_self_correcting_rag.py

    START → retrieve → grade ─┬─ relevant ─────────────▶ answer → END
                              ├─ not relevant, tries<2 ▶ rewrite → retrieve
                              └─ not relevant, tries=2 ▶ give_up → END

The grader catches bad retrievals BEFORE the model answers from the wrong text.
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from ops_buddy import policies
from ops_buddy.config import chat_model

llm = chat_model()
MAX_TRIES = 2


class State(TypedDict, total=False):
    question: str
    query: str
    chunks: list[dict]
    relevant: bool
    tries: int
    answer: str


class Grade(BaseModel):
    relevant: bool = Field(description="True only if the chunks contain the answer to the question.")
    reason: str


def retrieve(state: State) -> dict:
    query = state.get("query") or state["question"]
    chunks = policies.search(query, k=3)
    print(f"  retrieve({query!r}) -> {[c['source'] for c in chunks]}")
    return {"chunks": chunks, "tries": state.get("tries", 0) + 1}


def grade(state: State) -> dict:
    context = "\n".join(f"[{c['source']}] {c['text']}" for c in state["chunks"]) or "(nothing found)"
    g = llm.with_structured_output(Grade).invoke(
        f"Question: {state['question']}\n\nRetrieved text:\n{context}\n\nDoes this text answer the question?")
    print(f"  grade -> relevant={g.relevant} ({g.reason})")
    return {"relevant": g.relevant}


def rewrite(state: State) -> dict:
    new_query = llm.invoke(
        "Rewrite this question as a short keyword search query for an HR policy handbook. "
        "Use formal policy words (e.g. 'remote work', 'childcare', 'reimbursement'). "
        f"Reply with the query only.\n\nQuestion: {state['question']}\nPrevious query: {state.get('query')}").text
    print(f"  rewrite -> {new_query!r}")
    return {"query": new_query.strip()}


def answer(state: State) -> dict:
    context = "\n".join(f"[{c['source']}] {c['text']}" for c in state["chunks"])
    reply = llm.invoke(f"Answer using ONLY this policy text, citing sources in [brackets].\n\n{context}\n\n"
                       f"Question: {state['question']}").text
    return {"answer": reply}


def give_up(state: State) -> dict:
    return {"answer": "I couldn't find this in the policies. I've flagged it for the HR team."}


def after_grade(state: State) -> str:
    if state["relevant"]:
        return "answer"
    return "rewrite" if state["tries"] < MAX_TRIES else "give_up"


g = StateGraph(State)
for name, fn in [("retrieve", retrieve), ("grade", grade), ("rewrite", rewrite),
                 ("answer", answer), ("give_up", give_up)]:
    g.add_node(name, fn)
g.add_edge(START, "retrieve")
g.add_edge("retrieve", "grade")
g.add_conditional_edges("grade", after_grade, ["answer", "rewrite", "give_up"])
g.add_edge("rewrite", "retrieve")
g.add_edge("answer", END)
g.add_edge("give_up", END)
rag = g.compile()

for q in ["How do I claim my home internet bill?",
          "My son has a fever, can I log in from my flat today?",  # keyword search misses; rewrite should fix it
          "How many free lunches do we get per week?"]:  # not in the policies at all
    print(f"\nQUESTION: {q}")
    print(f"ANSWER: {rag.invoke({'question': q})['answer']}")
