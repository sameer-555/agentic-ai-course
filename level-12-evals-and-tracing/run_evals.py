"""Run every test case through the agent, score it, save the traces.

Run:  python level-12-evals-and-tracing/run_evals.py            (all cases)
      python level-12-evals-and-tracing/run_evals.py two-part   (one case by id)

Exits with code 1 if the pass rate is below THRESHOLD, so CI can block a bad change.
'security-other-employee' will probably FAIL: nothing in the code stops Ops Buddy reading another
employee's balance, so only the model's judgement stands in the way. Level 13 fixes it in code.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

from ops_buddy import data
from ops_buddy.agent import run_agent
from ops_buddy.config import MODEL, anthropic_client
from scorers import check_answer, check_trajectory, judge, tool_calls

HERE = Path(__file__).parent
THRESHOLD = 0.85


def load_cases(only=None):
    cases = [json.loads(line) for line in (HERE / "dataset.jsonl").read_text().splitlines() if line.strip()]
    return [c for c in cases if not only or c["id"] in only]


def main(only=None, agent=run_agent):
    client = anthropic_client()
    cases = load_cases(only)
    trace_file = HERE / "traces" / f"run-{datetime.now():%Y%m%d-%H%M%S}.jsonl"
    trace_file.parent.mkdir(exist_ok=True)
    passed = 0

    print(f"{'case':28s} {'tools called':45s} result")
    print("-" * 90)
    with trace_file.open("w") as f:
        for case in cases:
            data.reset()  # every case starts from the same database
            start = time.perf_counter()
            answer, trace = agent(case["input"], employee_id=case["employee_id"])
            seconds = time.perf_counter() - start

            fails = (check_answer(answer, case) + check_trajectory(trace, case)
                     + judge(answer, case, client, MODEL))
            passed += not fails
            names = " → ".join(c["tool"] for c in tool_calls(trace)) or "(none)"
            print(f"{case['id']:28s} {names[:45]:45s} {'PASS' if not fails else 'FAIL'}")
            for msg in fails:
                print(f"{'':28s}   ↳ {msg}")

            f.write(json.dumps({"case": case["id"], "input": case["input"], "answer": answer,
                                "trace": trace, "fails": fails, "seconds": round(seconds, 2)},
                               default=str) + "\n")

    rate = passed / len(cases)
    print("-" * 90)
    print(f"Passed {passed}/{len(cases)} = {rate:.0%} (threshold {THRESHOLD:.0%}).  Traces: {trace_file}")
    return rate


if __name__ == "__main__":
    rate = main(set(sys.argv[1:]) or None)
    sys.exit(0 if rate >= THRESHOLD else 1)
