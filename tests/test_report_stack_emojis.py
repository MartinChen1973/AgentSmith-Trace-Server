"""Tests for call-stack role emojis and DeepAgent display names."""

from agentsmith_trace_server.models import RunType
from agentsmith_trace_server.report_panels import render_runs_list


def test_call_stack_deepagent_shows_name_and_emoji() -> None:
    html = render_runs_list(
        [
            {
                "run_id": "root-1",
                "parent_run_id": None,
                "run_type": RunType.TOOL.value,
                "name": "turn_prompt",
                "start_time": "2026-07-26T10:00:00+00:00",
                "metadata": {
                    "activity_kind": "turn_prompt",
                    "deepagent": "build-requirement",
                },
            },
        ]
    )
    assert "🤖" in html
    assert "deep-agent" in html
    assert "build-requirement" in html
    head_idx = html.find("stack-summary-head")
    assert head_idx >= 0
    summary_snippet = html[head_idx : head_idx + 600]
    assert "build-requirement" in summary_snippet
    assert "turn_prompt" not in summary_snippet


def test_call_stack_subagent_and_skill_emojis() -> None:
    html = render_runs_list(
        [
            {
                "run_id": "root-1",
                "parent_run_id": None,
                "run_type": RunType.TOOL.value,
                "name": "turn_prompt",
                "start_time": "2026-07-26T10:00:00+00:00",
                "metadata": {"activity_kind": "turn_prompt", "deepagent": "default"},
            },
            {
                "run_id": "sub-1",
                "parent_run_id": "root-1",
                "run_type": RunType.TOOL.value,
                "name": "action-analyst",
                "start_time": "2026-07-26T10:00:01+00:00",
                "metadata": {
                    "activity_kind": "subagent_task",
                    "subagent_type": "action-analyst",
                    "phase": "completed",
                },
            },
            {
                "run_id": "skill-1",
                "parent_run_id": "sub-1",
                "run_type": RunType.TOOL.value,
                "name": "requirement-action",
                "start_time": "2026-07-26T10:00:02+00:00",
                "metadata": {
                    "activity_kind": "skill_used",
                    "skill_id": "requirement-action",
                    "tool_name": "read_file",
                },
            },
        ]
    )
    assert "🐜" in html
    assert "sub-agent" in html
    assert "action-analyst" in html
    assert "🛠️" in html
    assert "requirement-action" in html
