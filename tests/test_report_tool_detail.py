"""Tests for tool run detail rendering in the report conversation view."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from agentsmith_trace_server.api import create_app
from agentsmith_trace_server.models import RunEvent, RunStatus, RunType
from agentsmith_trace_server.report_panels import _format_tool_target_display


def test_format_tool_target_display_parent_and_file():
    assert _format_tool_target_display("/skills/foo/SKILL.md") == "foo/SKILL.md"
    assert _format_tool_target_display("/path/to/order_actions.md") == "to/order_actions.md"
    assert _format_tool_target_display("SKILL.md") == "SKILL.md"
    assert _format_tool_target_display("/large_tool_results/action-discovery-order.md") == (
        "large_tool_results/action-discovery-order.md"
    )


def test_read_file_tool_shows_short_path_from_inputs(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    thread_id = "thread_read_file"
    user_id = "usr_read"
    trace_id = uuid4()
    tool_run_id = uuid4()

    event = RunEvent(
        run_id=tool_run_id,
        trace_id=trace_id,
        run_type=RunType.TOOL,
        name="read_file",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        inputs={"file_path": "/skills/foo/SKILL.md"},
        outputs={"output": "ok"},
        metadata={"user_id": user_id, "thread_id": thread_id},
    )
    client.post("/api/v1/runs", json=event.model_dump(mode="json"))

    report = client.get(f"/report?user_id={user_id}&thread_id={thread_id}")
    assert report.status_code == 200
    assert '<code class="bubble-param">foo/SKILL.md</code>' in report.text
    assert "bubble-main" in report.text


def test_read_file_activity_shows_short_path_from_args_preview(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    thread_id = "thread_read_preview"
    user_id = "usr_read"
    trace_id = uuid4()
    run_id = uuid4()
    file_path = "/path/to/order_actions.md"

    event = RunEvent(
        run_id=run_id,
        trace_id=trace_id,
        run_type=RunType.TOOL,
        name="read_file",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        inputs={
            "payload": {
                "tool_name": "read_file",
                "args_preview": f"{{'file_path': '{file_path}'}}",
                "source": "seai_activity",
            }
        },
        metadata={
            "user_id": user_id,
            "thread_id": thread_id,
            "activity_kind": "tool_used",
            "tool_name": "read_file",
            "args_preview": f"{{'file_path': '{file_path}'}}",
        },
    )
    client.post("/api/v1/runs", json=event.model_dump(mode="json"))

    report = client.get(f"/report?user_id={user_id}&thread_id={thread_id}")
    assert report.status_code == 200
    assert '<code class="bubble-param">to/order_actions.md</code>' in report.text
    assert "bubble-main" in report.text


def test_skill_used_read_file_shows_short_path_from_metadata(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    thread_id = "thread_skill_read"
    user_id = "usr_read"
    trace_id = uuid4()
    run_id = uuid4()
    skill_path = "/skills/scenario-discovery/SKILL.md"

    event = RunEvent(
        run_id=run_id,
        trace_id=trace_id,
        run_type=RunType.TOOL,
        name="scenario-discovery",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        inputs={"payload": {"skill_id": "scenario-discovery", "path": skill_path}},
        metadata={
            "user_id": user_id,
            "thread_id": thread_id,
            "activity_kind": "skill_used",
            "skill_id": "scenario-discovery",
            "tool_name": "read_file",
            "path": skill_path,
        },
    )
    client.post("/api/v1/runs", json=event.model_dump(mode="json"))

    report = client.get(f"/report?user_id={user_id}&thread_id={thread_id}")
    assert report.status_code == 200
    assert (
        '<code class="bubble-param">scenario-discovery/SKILL.md</code>' in report.text
    )
    assert "read_file" in report.text


def test_skill_read_collapses_duplicate_langchain_tool_row(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    thread_id = "thread_skill_dup"
    user_id = "usr_read"
    trace_id = uuid4()
    skill_path = "/skills/scenario-discovery/SKILL.md"

    langchain_tool = RunEvent(
        run_id=uuid4(),
        trace_id=trace_id,
        run_type=RunType.TOOL,
        name="read_file",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        inputs={"file_path": skill_path},
        metadata={"user_id": user_id, "thread_id": thread_id},
    )
    skill_event = RunEvent(
        run_id=uuid4(),
        trace_id=trace_id,
        run_type=RunType.TOOL,
        name="scenario-discovery",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        metadata={
            "user_id": user_id,
            "thread_id": thread_id,
            "activity_kind": "skill_used",
            "skill_id": "scenario-discovery",
            "tool_name": "read_file",
            "path": skill_path,
        },
    )
    client.post("/api/v1/runs", json=langchain_tool.model_dump(mode="json"))
    client.post("/api/v1/runs", json=skill_event.model_dump(mode="json"))

    report = client.get(f"/report?user_id={user_id}&thread_id={thread_id}")
    assert report.status_code == 200
    assert "chat-avatar chat-avatar-tool chat-avatar-read_file" not in report.text
    assert "chat-avatar chat-avatar-tool chat-avatar-skill" in report.text
    assert "scenario-discovery · read_file" in report.text
    assert '<code class="bubble-param">scenario-discovery/SKILL.md</code>' in report.text
