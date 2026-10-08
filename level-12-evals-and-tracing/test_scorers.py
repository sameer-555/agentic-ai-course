"""Unit tests for the scorers. No API key needed: they use hand-written traces.

Run:  pytest level-12-evals-and-tracing -q

Test your test code! A buggy scorer gives you false confidence in a buggy agent.
"""

from scorers import check_answer, check_trajectory

TRACE = [
    {"step": 1, "tool": "check_leave_balance", "input": {"employee_id": "E1042"}, "output": {}},
    {"step": 2, "tool": "apply_leave", "input": {"employee_id": "E1042", "leave_date": "2026-10-09",
                                                 "leave_type": "casual"}, "output": {}},
    {"step": 3, "final": "Submitted LR-5531."},
]


def test_in_order_passes():
    assert check_trajectory(TRACE, {"expect_tools": ["check_leave_balance", "apply_leave"]}) == []


def test_wrong_order_fails():
    assert check_trajectory(TRACE, {"expect_tools": ["apply_leave", "check_leave_balance"]})


def test_any_order_passes():
    case = {"expect_tools": ["apply_leave", "check_leave_balance"], "order": "any"}
    assert check_trajectory(TRACE, case) == []


def test_forbidden_tool_fails():
    assert check_trajectory(TRACE, {"forbid_tools": ["apply_leave"]})


def test_expected_args():
    assert check_trajectory(TRACE, {"expect_args": {"apply_leave": {"leave_type": "casual"}}}) == []
    assert check_trajectory(TRACE, {"expect_args": {"apply_leave": {"leave_type": "sick"}}})


def test_forbidden_args():
    assert check_trajectory(TRACE, {"forbid_args": {"check_leave_balance": {"employee_id": "E1042"}}})
    assert check_trajectory(TRACE, {"forbid_args": {"check_leave_balance": {"employee_id": "E1043"}}}) == []


def test_max_tool_calls():
    assert check_trajectory(TRACE, {"max_tool_calls": 0})


def test_answer_is_case_insensitive():
    assert check_answer("Submitted lr-5531", {"answer_must_include": ["LR-"]}) == []
    assert check_answer("Done!", {"answer_must_include": ["LR-"]})
