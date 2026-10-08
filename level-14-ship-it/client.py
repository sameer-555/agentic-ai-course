"""A tiny terminal client for the streaming API.

Run (with the server running):
    python level-14-ship-it/client.py "Book casual leave this Friday"
    python level-14-ship-it/client.py --employee E1077 "Status of IT-3001?"
"""

import argparse
import json

import httpx

parser = argparse.ArgumentParser()
parser.add_argument("message")
parser.add_argument("--employee", default="E1042")
parser.add_argument("--session", default="cli")
parser.add_argument("--url", default="http://localhost:8000/chat")
args = parser.parse_args()

with httpx.stream("POST", args.url, json={"message": args.message, "session_id": args.session},
                  headers={"X-Employee-Id": args.employee}, timeout=120) as r:
    if r.status_code != 200:
        print(f"HTTP {r.status_code}: {r.read().decode()}")
        raise SystemExit(1)
    event = None
    for line in r.iter_lines():
        if line.startswith("event: "):
            event = line[7:]
        elif line.startswith("data: "):
            payload = json.loads(line[6:])
            if event == "text":
                print(payload, end="", flush=True)
            elif event == "tool":
                print(f"\n  [using {payload['name']}...]", flush=True)
            elif event == "error":
                print(f"\n  ERROR: {payload}")
            elif event == "done":
                print(f"\n  [done: {payload}]")
