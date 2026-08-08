"""Tests for two-line content preview in collapsed report UI."""

from agentsmith_trace_server.report_panels import (
    _two_line_ellipsis,
    render_conversation,
    render_run_panel,
    render_runs_list,
)


def test_two_line_ellipsis_splits_long_text() -> None:
    text = (
        "Entity Order needs CIDED CRUD actions. Follow the forced skill path and load skill "
        "references before naming. Analyze the entity 'Order' to determine the necessary CRUD "
        "actions using the CIDED template. After loading necessary skill references, generate "
        "specific actions associated with this entity. Use action_discovery_log when logging discoveries."
    )
    out = _two_line_ellipsis(text)
    lines = out.split("\n")
    assert len(lines) == 2
    assert lines[0].endswith("...")
    assert lines[1].startswith("...")
    assert lines[0].startswith("Entity Order")
    assert "discoveries." in lines[1]


def test_two_line_ellipsis_short_text_unchanged() -> None:
    text = "Short user prompt."
    assert _two_line_ellipsis(text) == text


def test_render_run_panel_shows_full_content_when_expanded() -> None:
    long_content = "A" * 60 + " middle omitted " + "B" * 60
    html = render_run_panel(
        {
            "run_id": "r1",
            "inputs": {"content": long_content},
            "outputs": {},
            "metadata": {},
        },
        show_detail_link=False,
    )
    assert long_content in html
    assert "...\n..." not in html


def test_call_stack_collapsed_shows_two_line_user_preview() -> None:
    long_content = (
        "Entity Order needs CIDED CRUD actions. Follow the forced skill path and load skill "
        "references before naming. Analyze the entity 'Order' to determine the necessary CRUD "
        "actions using the CIDED template. After loading necessary skill references, generate "
        "specific actions associated with this entity. Use action_discovery_log when logging discoveries."
    )
    html = render_runs_list(
        [
            {
                "run_id": "root-1",
                "parent_run_id": None,
                "run_type": "tool",
                "name": "user",
                "start_time": "2026-07-26T10:00:00+00:00",
                "inputs": {"content": long_content},
                "metadata": {"activity_kind": "user_message"},
            },
        ]
    )
    assert "stack-param-multiline" in html
    assert "Entity Order" in html
    assert "discoveries." in html
    assert "...\n..." in html or "..." in html


def test_chat_bubble_collapsed_has_preview_and_full_spans() -> None:
    long_content = "Start " + "x" * 140 + " End."
    html = render_conversation(
        [
            {
                "run_type": "tool",
                "name": "user",
                "start_time": "2026-07-26T10:00:00+00:00",
                "inputs": {"content": long_content},
                "metadata": {"activity_kind": "user_message"},
            },
        ]
    )
    assert "bubble-text-preview" in html
    assert "bubble-text-full" in html
    assert long_content in html
