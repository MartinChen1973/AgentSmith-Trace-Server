"""Tests for todo plan birth and outcome reconciliation panels."""

from __future__ import annotations

from agentsmith_trace_server.models import RunType
from agentsmith_trace_server.report_panels import render_runs_list
from agentsmith_trace_server.report_todos import (
    OUTCOME_ADDED,
    OUTCOME_DONE,
    OUTCOME_NOT_DONE,
    OUTCOME_REMOVED,
    aggregate_todo_timelines,
    reconcile_todos,
    todos_from_run,
)


def _todo_run(
    *,
    run_id: str,
    start_time: str,
    todos: list[dict[str, str]],
    phase: str | None = None,
    plan_phase: str | None = None,
    subagent_type: str = "action-analyst",
) -> dict:
    meta: dict = {
        "activity_kind": "deep_agent_todos",
        "tool_name": "write_todos",
        "agent_scope": "subagent",
        "subagent_type": subagent_type,
    }
    if phase:
        meta["phase"] = phase
    if plan_phase:
        meta["plan_phase"] = plan_phase
    return {
        "run_id": run_id,
        "parent_run_id": "root-1",
        "run_type": RunType.TOOL.value,
        "name": "write_todos",
        "start_time": start_time,
        "inputs": {"args": {"todos": todos}},
        "metadata": meta,
    }


def test_reconcile_todos_marks_done_and_not_done() -> None:
    birth = [
        {"content": "Analyze Order", "status": "pending"},
        {"content": "Write markdown", "status": "pending"},
    ]
    final = [
        {"content": "Analyze Order", "status": "completed"},
        {"content": "Write markdown", "status": "in_progress"},
    ]
    rows = reconcile_todos(birth, final)
    by_content = {row.content: row.outcome for row in rows}
    assert by_content["Analyze Order"] == OUTCOME_DONE
    assert by_content["Write markdown"] == OUTCOME_NOT_DONE


def test_reconcile_todos_detects_added_and_removed() -> None:
    birth = [
        {"content": "Task A", "status": "pending"},
        {"content": "Task B", "status": "pending"},
    ]
    final = [
        {"content": "Task A", "status": "completed"},
        {"content": "Task C", "status": "completed"},
    ]
    rows = reconcile_todos(birth, final)
    by_content = {row.content: row.outcome for row in rows}
    assert by_content["Task A"] == OUTCOME_DONE
    assert by_content["Task B"] == OUTCOME_REMOVED
    assert by_content["Task C"] == OUTCOME_ADDED


def test_aggregate_todo_timelines_uses_birth_and_final_snapshots() -> None:
    runs = [
        {
            "run_id": "root-1",
            "parent_run_id": None,
            "run_type": RunType.TOOL.value,
            "name": "turn_prompt",
            "start_time": "2026-07-26T10:00:00+00:00",
            "metadata": {"activity_kind": "turn_prompt", "deepagent": "build-requirement"},
        },
        _todo_run(
            run_id="todo-start",
            start_time="2026-07-26T10:00:01+00:00",
            todos=[
                {"content": "Plan step", "status": "pending"},
                {"content": "Later step", "status": "pending"},
            ],
            phase="started",
            plan_phase="initial",
        ),
        _todo_run(
            run_id="todo-end",
            start_time="2026-07-26T10:00:05+00:00",
            todos=[
                {"content": "Plan step", "status": "completed"},
                {"content": "Later step", "status": "pending"},
            ],
            phase="completed",
            plan_phase="initial",
        ),
    ]
    timelines = aggregate_todo_timelines(runs)
    assert len(timelines) == 1
    timeline = timelines[0]
    assert timeline.owner_label == "Sub-agent · action-analyst"
    assert todos_from_run(timeline.birth_run)[0]["content"] == "Plan step"
    assert timeline.outcomes[0].outcome == OUTCOME_DONE
    assert timeline.outcomes[1].outcome == OUTCOME_NOT_DONE


def test_render_runs_list_includes_plan_and_outcome_panels() -> None:
    runs = [
        {
            "run_id": "root-1",
            "parent_run_id": None,
            "run_type": RunType.TOOL.value,
            "name": "turn_prompt",
            "start_time": "2026-07-26T10:00:00+00:00",
            "metadata": {"activity_kind": "turn_prompt", "deepagent": "build-requirement"},
        },
        _todo_run(
            run_id="todo-start",
            start_time="2026-07-26T10:00:01+00:00",
            todos=[{"content": "Birth task", "status": "pending"}],
            phase="started",
            plan_phase="initial",
        ),
        _todo_run(
            run_id="todo-end",
            start_time="2026-07-26T10:00:02+00:00",
            todos=[{"content": "Birth task", "status": "completed"}],
            phase="completed",
            plan_phase="initial",
        ),
    ]
    html = render_runs_list(runs)
    assert "todo-plan-panel" in html
    assert "Plan (at birth)" in html
    assert "Birth task" in html
    assert "todo-outcome-panel" in html
    assert "Outcome (planned vs final)" in html
    assert "Completed as planned" in html
    assert html.index("todo-plan-panel") < html.index("call-stack-root")
    assert html.index("call-stack-root") < html.index("todo-outcome-panel")
