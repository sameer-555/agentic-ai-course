"""API tests that need no API key: auth, budget, health.

Run:  pytest level-14-ship-it -q
"""

from datetime import date

from fastapi.testclient import TestClient

import app as server

client = TestClient(server.app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_unknown_employee_is_rejected():
    r = client.post("/chat", json={"message": "hi"}, headers={"X-Employee-Id": "E9999"})
    assert r.status_code == 401


def test_missing_header_is_rejected():
    assert client.post("/chat", json={"message": "hi"}).status_code == 401


def test_daily_cost_cap_blocks_before_calling_the_model():
    server.SPEND[("E1042", date.today())] = server.DAILY_COST_CAP_USD
    try:
        r = client.post("/chat", json={"message": "hi"}, headers={"X-Employee-Id": "E1042"})
        assert r.status_code == 429
    finally:
        server.SPEND.clear()


def test_cost_maths():
    class Usage:
        input_tokens, output_tokens = 1_000_000, 100_000
    assert round(server.cost_usd(Usage), 2) == 7.50  # 1M in at $5 + 0.1M out at $25
