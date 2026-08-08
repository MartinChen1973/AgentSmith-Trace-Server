"""Tests for todo list logging and collapsed display in report UI."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from agentsmith_trace_server.api import create_app
from agentsmith_trace_server.models import RunEvent, RunStatus, RunType
from agentsmith_trace_server.report_panels import _todos_from_run, render_runs_list


def test_todos_from_run_reads_nested_args() -> None:
    todos = [
        {"content": "Step one", "status": "pending"},
        {"content": "Step two", "status": "in_progress"},
    ]
    run = {
        "inputs": {
            "args": {"todos": todos},
        }
    }
    assert _todos_from_run(run) == todos


def test_call_stack_collapsed_shows_full_todo_list() -> None:
    todos = [
        {"content": "Load requirement pipeline skill", "status": "pending"},
        {"content": "Delegate scenario analyst", "status": "in_progress"},
        {"content": "Human review gate", "status": "pending"},
    ]
    html = render_runs_list(
        [
            {
                "run_id": "root-1",
                "parent_run_id": None,
                "run_type": RunType.TOOL.value,
                "name": "turn_prompt",
                "start_time": "2026-07-26T10:00:00+00:00",
                "metadata": {"activity_kind": "turn_prompt", "deepagent": "build-requirement"},
            },
            {
                "run_id": "todo-1",
                "parent_run_id": "root-1",
                "run_type": RunType.TOOL.value,
                "name": "write_todos",
                "start_time": "2026-07-26T10:00:01+00:00",
                "inputs": {"todos": todos},
                "metadata": {"activity_kind": "deep_agent_todos", "tool_name": "write_todos"},
            },
        ]
    )
    assert "stack-summary-todos" in html
    assert "todo-list-full" in html
    assert "Load requirement pipeline skill" in html
    assert "Human review gate" in html
    assert html.index("stack-summary-head") < html.index("stack-summary-todos")


def test_report_page_shows_todos_when_collapsed(tmp_path) -> None:
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    thread_id = "thread_todos"
    user_id = "usr_todos"
    trace_id = uuid4()
    todos = [
        {"content": "Todo A", "status": "pending"},
        {"content": "Todo B", "status": "completed"},
    ]
    event = RunEvent(
        run_id=uuid4(),
        trace_id=trace_id,
        run_type=RunType.TOOL,
        name="write_todos",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        inputs={"todos": todos},
        metadata={
            "user_id": user_id,
            "thread_id": thread_id,
            "activity_kind": "deep_agent_todos",
            "tool_name": "write_todos",
        },
    )
    client.post("/api/v1/runs", json=event.model_dump(mode="json"))
    report = client.get(f"/report?user_id={user_id}&thread_id={thread_id}")
    assert report.status_code == 200
    assert "bubble-todos" in report.text
    assert "Todo A" in report.text
    assert "Todo B" in report.text
    assert "completed" in report.text
