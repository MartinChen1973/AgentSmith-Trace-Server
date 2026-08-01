"""Tests for per-tool emoji avatars in the report conversation view."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from agentsmith_trace_server.api import create_app
from agentsmith_trace_server.models import RunEvent, RunStatus, RunType
from agentsmith_trace_server.report_tool_icons import (
    ICON_KIND_READ_FILE,
    ICON_KIND_SKILL,
    ICON_KIND_WRITE_FILE,
    ICON_KIND_WRITE_TODOS,
    tool_icon_kind,
)


def test_tool_icon_kind_mapping():
    read_run = {
        "name": "read_file",
        "metadata": {"activity_kind": "tool_used", "tool_name": "read_file"},
    }
    write_run = {
        "name": "write_file",
        "metadata": {"activity_kind": "tool_used", "tool_name": "write_file"},
    }
    skill_run = {
        "name": "scenario-discovery",
        "metadata": {
            "activity_kind": "skill_used",
            "tool_name": "read_file",
            "skill_id": "scenario-discovery",
        },
    }
    todos_run = {
        "name": "write_todos",
        "metadata": {"activity_kind": "deep_agent_todos", "tool_name": "write_todos"},
    }
    langchain_todos = {"name": "write_todos", "metadata": {"thread_id": "t1"}}

    assert tool_icon_kind(read_run) == ICON_KIND_READ_FILE
    assert tool_icon_kind(write_run) == ICON_KIND_WRITE_FILE
    assert tool_icon_kind(skill_run) == ICON_KIND_SKILL
    assert tool_icon_kind(todos_run) == ICON_KIND_WRITE_TODOS
    assert tool_icon_kind(langchain_todos) == ICON_KIND_WRITE_TODOS


def test_activity_rows_show_inline_tool_icons(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    thread_id = "thread_icons"
    user_id = "usr_icons"
    trace_id = uuid4()

    runs = [
        RunEvent(
            run_id=uuid4(),
            trace_id=trace_id,
            run_type=RunType.TOOL,
            name="read_file",
            status=RunStatus.SUCCESS,
            start_time=datetime.now(timezone.utc),
            inputs={"file_path": "/skills/foo/SKILL.md"},
            metadata={
                "user_id": user_id,
                "thread_id": thread_id,
                "activity_kind": "tool_used",
                "tool_name": "read_file",
            },
        ),
        RunEvent(
            run_id=uuid4(),
            trace_id=trace_id,
            run_type=RunType.TOOL,
            name="write_file",
            status=RunStatus.SUCCESS,
            start_time=datetime.now(timezone.utc),
            inputs={"file_path": "/tmp/out.md"},
            metadata={
                "user_id": user_id,
                "thread_id": thread_id,
                "activity_kind": "tool_used",
                "tool_name": "write_file",
            },
        ),
        RunEvent(
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
                "tool_name": "read_file",
                "skill_id": "scenario-discovery",
                "path": "/skills/scenario-discovery/SKILL.md",
            },
        ),
        RunEvent(
            run_id=uuid4(),
            trace_id=trace_id,
            run_type=RunType.TOOL,
            name="write_todos",
            status=RunStatus.SUCCESS,
            start_time=datetime.now(timezone.utc),
            inputs={
                "todos": [
                    {
                        "content": "Analyze the entity Order",
                        "status": "in_progress",
                    }
                ]
            },
            metadata={"user_id": user_id, "thread_id": thread_id},
        ),
    ]
    for event in runs:
        client.post("/api/v1/runs", json=event.model_dump(mode="json"))

    report = client.get(f"/report?user_id={user_id}&thread_id={thread_id}")
    assert report.status_code == 200
    assert "chat-avatar-read_file" in report.text
    assert "chat-avatar-write_file" in report.text
    assert "chat-avatar-skill" in report.text
    assert "avatar-emoji" in report.text
    assert "chat-avatar-write_todos" in report.text
    assert "todo-list" in report.text
    assert "Analyze the entity Order" in report.text
    assert "in_progress" in report.text
