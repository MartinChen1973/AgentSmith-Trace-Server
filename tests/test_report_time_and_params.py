"""Tests for relative timestamps and param display in report panels."""

from __future__ import annotations

from datetime import datetime, timezone

from agentsmith_trace_server.models import RunType
from agentsmith_trace_server.report_panels import (
    _format_event_time,
    _status_merge_html,
    _thread_anchor_time,
    render_conversation,
    render_runs_list,
)


def test_status_merge_success_shows_pending_arrow_success():
    html = _status_merge_html(
        {
            "status": "success",
            "end_time": "2026-07-26T10:00:01+00:00",
            "metadata": {"duration_ms": 352},
        }
    )
    assert "status-merge" in html
    assert "status-pending" in html
    assert "status-success" in html
    assert "→" in html
    assert "pending → success" in html
    assert "352 ms" in html


def test_status_merge_success_without_end_time():
    html = _status_merge_html({"status": "success"})
    assert "status-merge" in html
    assert "pending" in html and "success" in html


def test_status_merge_pending_only_while_running():
    html = _status_merge_html({"status": "pending"})
    assert "status-pending" in html
    assert "status-merge" not in html
    assert "Still running" in html


def test_status_merge_pending_after_turn_finished():
    html = _status_merge_html({"status": "pending"}, thread_finished=True)
    assert "status-merge" in html
    assert "Turn finished" in html


def test_format_event_time_anchor_and_delta():
    anchor = datetime(2026, 7, 26, 10, 0, 0, tzinfo=timezone.utc)
    first = "2026-07-26T10:00:00+00:00"
    later = "2026-07-26T10:00:03.52+00:00"
    assert _format_event_time(first, anchor) == "2026-07-26 10:00:00"
    assert _format_event_time(later, anchor) == "+3.52s"


def test_conversation_shows_relative_time_on_later_bubbles():
    runs = [
        {
            "run_type": RunType.TOOL.value,
            "name": "user",
            "start_time": "2026-07-26T10:00:00+00:00",
            "inputs": {"content": "hello"},
            "metadata": {"activity_kind": "user_message"},
        },
        {
            "run_type": RunType.TOOL.value,
            "name": "write_todos",
            "start_time": "2026-07-26T10:00:02.5+00:00",
            "status": "success",
            "metadata": {"activity_kind": "deep_agent_todos", "deepagent": "append-requirement"},
        },
    ]
    html = render_conversation(runs)
    assert "2026-07-26 10:00:00" in html
    assert "+2.50s" in html


def test_call_stack_shows_param_and_relative_time():
    runs = [
            {
                "run_id": "root-1",
                "parent_run_id": None,
                "run_type": RunType.TOOL.value,
                "name": "turn_prompt",
                "start_time": "2026-07-26T10:00:00+00:00",
                "end_time": "2026-07-26T10:00:05+00:00",
                "status": "success",
                "metadata": {"activity_kind": "turn_prompt", "deepagent": "build-requirement"},
            },
            {
                "run_id": "tool-1",
                "parent_run_id": "root-1",
                "run_type": RunType.TOOL.value,
                "name": "read_file",
                "start_time": "2026-07-26T10:00:01.25+00:00",
                "end_time": "2026-07-26T10:00:01.5+00:00",
                "status": "success",
            "inputs": {"file_path": "/skills/foo/SKILL.md"},
            "metadata": {
                "activity_kind": "tool_used",
                "tool_name": "read_file",
            },
        },
    ]
    html = render_runs_list(runs)
    assert "call-stack-root" in html
    assert "/skills/foo/SKILL.md" in html
    assert "stack-param-line" in html
    assert "stack-summary-head" in html
    assert "stack-summary-end" in html
    assert "status-merge" in html
    assert "2026-07-26 10:00:00" in html
    assert "+1.25s" in html


def test_activity_chip_has_status_merge_and_param_tooltip(tmp_path):
    from uuid import uuid4

    from fastapi.testclient import TestClient

    from agentsmith_trace_server.api import create_app
    from agentsmith_trace_server.models import RunEvent, RunStatus

    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    thread_id = "thread_tip"
    user_id = "usr_tip"
    path = "/skills/foo/SKILL.md"
    event = RunEvent(
        run_id=uuid4(),
        trace_id=uuid4(),
        run_type=RunType.TOOL,
        name="read_file",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        inputs={"file_path": path},
        metadata={"user_id": user_id, "thread_id": thread_id, "tool_name": "read_file"},
    )
    client.post("/api/v1/runs", json=event.model_dump(mode="json"))
    report = client.get(f"/report?user_id={user_id}&thread_id={thread_id}")
    assert report.status_code == 200
    assert "status-merge" in report.text
    assert f'title="{path}"' in report.text
    assert "has-tip" in report.text


def test_llm_stack_detail_tool_calls():
    from agentsmith_trace_server.report_panels import _llm_stack_detail

    detail = _llm_stack_detail(
        {
            "run_type": RunType.LLM.value,
            "outputs": {
                "content": "",
                "tool_calls": [
                    {
                        "name": "task",
                        "args": {"subagent_type": "action-analyst"},
                    }
                ],
            },
        }
    )
    assert detail is not None
    assert "task" in detail
    assert "action-analyst" in detail


def test_call_stack_subagent_description_on_second_row():
    desc = (
        "Analyze the entity 'Order' to determine necessary CRUD actions "
        "using the CIDED template. Follow the standard process outlined in the skill."
    )
    runs = [
        {
            "run_id": "root-1",
            "parent_run_id": None,
            "run_type": RunType.TOOL.value,
            "name": "turn_prompt",
            "start_time": "2026-07-26T10:00:00+00:00",
            "end_time": "2026-07-26T10:01:00+00:00",
            "status": "success",
            "metadata": {"activity_kind": "turn_prompt", "deepagent": "build-requirement"},
        },
        {
            "run_id": "sub-1",
            "parent_run_id": "root-1",
            "run_type": RunType.TOOL.value,
            "name": "action-analyst",
            "start_time": "2026-07-26T10:00:01+00:00",
            "end_time": "2026-07-26T10:00:05+00:00",
            "status": "success",
            "metadata": {
                "activity_kind": "subagent_task",
                "subagent_type": "action-analyst",
                "phase": "completed",
                "description": desc,
            },
            "inputs": {"description": desc},
        },
    ]
    html = render_runs_list(runs)
    assert "stack-summary-param" in html
    assert "stack-param-line" in html
    assert "Analyze the entity" in html
    assert html.index("stack-summary-head") < html.index("stack-summary-param")
    assert html.index("status-merge") < html.index("stack-summary-param")


def test_thread_anchor_time_min_start():
    runs = [
        {"start_time": "2026-07-26T10:00:05+00:00"},
        {"start_time": "2026-07-26T10:00:00+00:00"},
    ]
    anchor = _thread_anchor_time(runs)
    assert anchor is not None
    assert anchor == datetime(2026, 7, 26, 10, 0, 0, tzinfo=timezone.utc)
