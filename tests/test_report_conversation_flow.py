"""Tests for conversation ordering: user → DeepAgent invoke → assistant → tools."""

from __future__ import annotations

from agentsmith_trace_server.models import RunType
from agentsmith_trace_server.report_panels import render_conversation


def _pos(html: str, needle: str) -> int:
    idx = html.find(needle)
    assert idx >= 0, f"missing {needle!r} in report HTML"
    return idx


def test_conversation_order_user_deepagent_then_tools():
    user_text = "Analyze the entity Order"
    runs = [
        {
            "run_type": RunType.TOOL.value,
            "name": "write_todos",
            "start_time": "2026-07-26T10:00:02+00:00",
            "status": "success",
            "metadata": {
                "activity_kind": "deep_agent_todos",
                "deepagent": "append-requirement",
            },
        },
        {
            "run_type": RunType.TOOL.value,
            "name": "turn_prompt",
            "start_time": "2026-07-26T10:00:01+00:00",
            "status": "success",
            "metadata": {
                "activity_kind": "turn_prompt",
                "deepagent": "append-requirement",
                "agent_scope": "deep_agent",
                "agent_name": "append-requirement",
            },
        },
        {
            "run_type": RunType.TOOL.value,
            "name": "user",
            "start_time": "2026-07-26T10:00:00+00:00",
            "status": "success",
            "inputs": {"content": user_text},
            "metadata": {
                "activity_kind": "user_message",
                "deepagent": "append-requirement",
            },
        },
    ]
    html = render_conversation(runs)
    assert '<span class="speaker">User</span>' in html
    assert '<span class="speaker">DeepAgent · append-requirement</span>' in html
    assert "invoked" in html
    assert _pos(html, user_text) < _pos(html, "invoked")
    assert _pos(html, "invoked") < _pos(html, "tool: write_todos")


def test_subagent_llm_task_prompt_not_shown_as_user():
    user_text = "Entity Order needs CIDED CRUD actions from the user."
    subagent_task = (
        "Analyze the entity 'Order' using the CIDED template "
        "(internal sub-agent task, not typed by the user)."
    )
    runs = [
        {
            "run_type": RunType.TOOL.value,
            "name": "user",
            "start_time": "2026-07-26T10:00:00+00:00",
            "inputs": {"content": user_text},
            "metadata": {"activity_kind": "user_message"},
        },
        {
            "run_type": RunType.LLM.value,
            "name": "ChatOpenAI",
            "start_time": "2026-07-26T10:00:02+00:00",
            "inputs": {"messages": [{"role": "user", "content": subagent_task}]},
            "outputs": {"content": "routing"},
            "metadata": {"agent_scope": "subagent", "subagent_type": "action-analyst"},
        },
    ]
    html = render_conversation(runs)
    assert html.count('<span class="speaker">User</span>') == 1
    assert user_text in html
    assert subagent_task not in html


def test_user_message_dedupes_llm_user_bubble():
    user_text = "Same prompt twice"
    runs = [
        {
            "run_type": RunType.TOOL.value,
            "name": "user",
            "start_time": "2026-07-26T10:00:00+00:00",
            "inputs": {"content": user_text},
            "metadata": {"activity_kind": "user_message"},
        },
        {
            "run_type": RunType.LLM.value,
            "name": "ChatOpenAI",
            "start_time": "2026-07-26T10:00:01+00:00",
            "inputs": {"messages": [{"role": "user", "content": user_text}]},
            "outputs": {"content": "ok"},
            "metadata": {},
        },
    ]
    html = render_conversation(runs)
    assert html.count(user_text) == 1
