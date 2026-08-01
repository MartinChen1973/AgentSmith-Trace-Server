"""Tests for DeepAgent / sub-agent speaker labels in conversation view."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from agentsmith_trace_server.api import create_app
from agentsmith_trace_server.models import RunEvent, RunStatus, RunType
from agentsmith_trace_server.report_agent_labels import (
    AgentConversationContext,
    assistant_speaker_label,
    deepagent_invoke_speaker_label,
    update_agent_context,
)


def test_assistant_label_from_deepagent_metadata():
    run = {
        "name": "ChatOpenAI",
        "metadata": {"deepagent": "append-requirement"},
    }
    label = assistant_speaker_label(run, AgentConversationContext())
    assert label == "DeepAgent · append-requirement"


def test_deepagent_invoke_label():
    run = {
        "metadata": {
            "deepagent": "append-requirement",
            "agent_scope": "deep_agent",
            "agent_name": "append-requirement",
        }
    }
    label = deepagent_invoke_speaker_label(run, AgentConversationContext())
    assert label == "DeepAgent · append-requirement"


def test_assistant_label_from_active_subagent_context():
    ctx = AgentConversationContext(deepagent="append-requirement")
    update_agent_context(
        ctx,
        {
            "metadata": {
                "activity_kind": "subagent_task",
                "phase": "started",
                "subagent_type": "scenario-analyst",
            }
        },
    )
    run = {"name": "ChatOpenAI", "metadata": {}}
    assert assistant_speaker_label(run, ctx) == "Sub-agent · scenario-analyst"


def test_report_shows_deepagent_and_subagent_speakers(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)
    thread_id = "thread_speakers"
    user_id = "usr_speakers"
    trace_id = uuid4()

    deep_llm = RunEvent(
        run_id=uuid4(),
        trace_id=trace_id,
        run_type=RunType.LLM,
        name="ChatOpenAI",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        inputs={"messages": [{"role": "user", "content": "go"}]},
        outputs={"content": "routing"},
        metadata={
            "user_id": user_id,
            "thread_id": thread_id,
            "deepagent": "append-requirement",
        },
    )
    sub_start = RunEvent(
        run_id=uuid4(),
        trace_id=trace_id,
        run_type=RunType.TOOL,
        name="scenario-analyst",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        metadata={
            "user_id": user_id,
            "thread_id": thread_id,
            "activity_kind": "subagent_task",
            "phase": "started",
            "subagent_type": "scenario-analyst",
            "deepagent": "append-requirement",
        },
    )
    sub_llm = RunEvent(
        run_id=uuid4(),
        trace_id=trace_id,
        run_type=RunType.LLM,
        name="ChatOpenAI",
        status=RunStatus.SUCCESS,
        start_time=datetime.now(timezone.utc),
        inputs={"messages": [{"role": "user", "content": "analyze"}]},
        outputs={"content": "scenario draft"},
        metadata={"user_id": user_id, "thread_id": thread_id},
    )
    for event in (deep_llm, sub_start, sub_llm):
        client.post("/api/v1/runs", json=event.model_dump(mode="json"))

    report = client.get(f"/report?user_id={user_id}&thread_id={thread_id}")
    assert report.status_code == 200
    assert "DeepAgent · append-requirement" in report.text
    assert "Sub-agent · scenario-analyst" in report.text
    assert '<span class="speaker">DeepAgent · append-requirement</span>' in report.text
    assert '<span class="speaker">Sub-agent · scenario-analyst</span>' in report.text
