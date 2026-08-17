"""Todo plan birth, revision timeline, and outcome reconciliation for Trace reports."""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from typing import Any

from agentsmith_trace_server.report_call_stack import (
    KIND_TODOS,
    metadata_of,
    parse_time,
)
from agentsmith_trace_server.report_tool_icons import (
    ACTIVITY_TODOS,
    ICON_KIND_WRITE_TODOS,
    tool_icon_kind,
)

PLAN_PHASE_INITIAL = "initial"
PLAN_PHASE_UPDATE = "update"
PHASE_STARTED = "started"
PHASE_COMPLETED = "completed"

OUTCOME_DONE = "done"
OUTCOME_NOT_DONE = "not_done"
OUTCOME_ADDED = "added"
OUTCOME_REMOVED = "removed"
OUTCOME_REVISED = "revised"

OUTCOME_LABELS = {
    OUTCOME_DONE: "Completed as planned",
    OUTCOME_NOT_DONE: "Not finished",
    OUTCOME_ADDED: "Added during run",
    OUTCOME_REMOVED: "Removed from plan",
    OUTCOME_REVISED: "Revised (same intent, new wording)",
}


def esc(value: Any) -> str:
    return html.escape(str(value))


def todos_from_run(run: dict[str, Any]) -> list[dict[str, Any]]:
    inputs = run.get("inputs")
    if isinstance(inputs, dict):
        payload = inputs.get("payload")
        if isinstance(payload, dict):
            args = payload.get("args")
            if isinstance(args, dict):
                nested = args.get("todos")
                if isinstance(nested, list):
                    return [t for t in nested if isinstance(t, dict)]
        todos = inputs.get("todos")
        if isinstance(todos, list):
            return [t for t in todos if isinstance(t, dict)]
        args = inputs.get("args")
        if isinstance(args, dict):
            nested = args.get("todos")
            if isinstance(nested, list):
                return [t for t in nested if isinstance(t, dict)]
    meta = run.get("metadata")
    if isinstance(meta, dict):
        args = meta.get("args")
        if isinstance(args, dict):
            nested = args.get("todos")
            if isinstance(nested, list):
                return [t for t in nested if isinstance(t, dict)]
    return []


def is_todo_run(run: dict[str, Any]) -> bool:
    meta = metadata_of(run)
    kind = str(meta.get("activity_kind") or "").strip()
    if kind == KIND_TODOS or kind == ACTIVITY_TODOS:
        return True
    return tool_icon_kind(run) == ICON_KIND_WRITE_TODOS


def _owner_key(meta: dict[str, Any]) -> str:
    scope = str(meta.get("agent_scope") or "deep_agent").strip()
    name = (
        meta.get("subagent_type")
        or meta.get("agent_name")
        or meta.get("deepagent")
        or "unknown"
    )
    return f"{scope}:{str(name).strip()}"


def owner_label(meta: dict[str, Any]) -> str:
    scope = str(meta.get("agent_scope") or "").strip()
    name = (
        meta.get("subagent_type")
        or meta.get("agent_name")
        or meta.get("deepagent")
    )
    if scope == "subagent" and isinstance(name, str) and name.strip():
        return f"Sub-agent · {name.strip()}"
    if isinstance(name, str) and name.strip():
        return f"DeepAgent · {name.strip()}"
    return "Agent"


def _normalize_content(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _todo_content(todo: dict[str, Any]) -> str:
    return str(todo.get("content") or "").strip()


def _todo_status(todo: dict[str, Any]) -> str:
    return str(todo.get("status") or "").strip().lower()


def _sort_key(run: dict[str, Any]) -> tuple:
    t = parse_time(run.get("start_time"))
    return (t, str(run.get("run_id") or ""))


@dataclass
class TodoOutcomeRow:
    content: str
    outcome: str
    birth_status: str = ""
    final_status: str = ""


@dataclass
class TodoOwnerTimeline:
    owner_key: str
    owner_label: str
    birth_run: dict[str, Any]
    final_run: dict[str, Any]
    revision_count: int
    outcomes: list[TodoOutcomeRow] = field(default_factory=list)


def _pick_birth_run(runs: list[dict[str, Any]]) -> dict[str, Any]:
    for run in runs:
        meta = metadata_of(run)
        if meta.get("plan_phase") == PLAN_PHASE_INITIAL and meta.get("phase") == PHASE_STARTED:
            return run
    for run in runs:
        meta = metadata_of(run)
        if meta.get("plan_phase") == PLAN_PHASE_INITIAL:
            return run
    for run in runs:
        meta = metadata_of(run)
        if meta.get("phase") == PHASE_STARTED:
            return run
    return runs[0]


def _pick_final_run(runs: list[dict[str, Any]]) -> dict[str, Any]:
    for run in reversed(runs):
        meta = metadata_of(run)
        if meta.get("phase") == PHASE_COMPLETED:
            return run
    return runs[-1]


def reconcile_todos(
    birth_todos: list[dict[str, Any]],
    final_todos: list[dict[str, Any]],
) -> list[TodoOutcomeRow]:
    birth_by_key: dict[str, dict[str, Any]] = {}
    for todo in birth_todos:
        content = _todo_content(todo)
        if content:
            birth_by_key[_normalize_content(content)] = todo

    final_by_key: dict[str, dict[str, Any]] = {}
    for todo in final_todos:
        content = _todo_content(todo)
        if content:
            final_by_key[_normalize_content(content)] = todo

    rows: list[TodoOutcomeRow] = []
    seen_final: set[str] = set()

    for key, birth in birth_by_key.items():
        final = final_by_key.get(key)
        content = _todo_content(birth)
        birth_status = _todo_status(birth)
        if final is None:
            rows.append(
                TodoOutcomeRow(
                    content=content,
                    outcome=OUTCOME_REMOVED,
                    birth_status=birth_status,
                )
            )
            continue
        seen_final.add(key)
        final_status = _todo_status(final)
        if final_status == "completed":
            rows.append(
                TodoOutcomeRow(
                    content=content,
                    outcome=OUTCOME_DONE,
                    birth_status=birth_status,
                    final_status=final_status,
                )
            )
        else:
            rows.append(
                TodoOutcomeRow(
                    content=content,
                    outcome=OUTCOME_NOT_DONE,
                    birth_status=birth_status,
                    final_status=final_status,
                )
            )

    for key, final in final_by_key.items():
        if key in seen_final:
            continue
        rows.append(
            TodoOutcomeRow(
                content=_todo_content(final),
                outcome=OUTCOME_ADDED,
                final_status=_todo_status(final),
            )
        )

    return rows


def aggregate_todo_timelines(runs: list[dict[str, Any]]) -> list[TodoOwnerTimeline]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        if not is_todo_run(run):
            continue
        key = _owner_key(metadata_of(run))
        grouped.setdefault(key, []).append(run)

    timelines: list[TodoOwnerTimeline] = []
    for owner_key, owner_runs in grouped.items():
        ordered = sorted(owner_runs, key=_sort_key)
        if not ordered:
            continue
        birth = _pick_birth_run(ordered)
        final = _pick_final_run(ordered)
        meta = metadata_of(birth)
        birth_todos = todos_from_run(birth)
        final_todos = todos_from_run(final)
        timelines.append(
            TodoOwnerTimeline(
                owner_key=owner_key,
                owner_label=owner_label(meta),
                birth_run=birth,
                final_run=final,
                revision_count=len(ordered),
                outcomes=reconcile_todos(birth_todos, final_todos),
            )
        )

    timelines.sort(key=lambda row: _sort_key(row.birth_run))
    return timelines


def _todos_list_html(
    todos: list[dict[str, Any]],
    *,
    css_class: str = "todo-list compact todo-list-full",
) -> str:
    if not todos:
        return ""
    items: list[str] = []
    for todo in todos:
        content = _todo_content(todo)
        if not content:
            continue
        status = str(todo.get("status") or "").strip()
        status_html = (
            f'<span class="todo-status">{esc(status)}</span>' if status else ""
        )
        items.append(f'<li class="todo-item">{status_html}<span>{esc(content)}</span></li>')
    if not items:
        return ""
    return f'<ul class="{esc(css_class)}">{"".join(items)}</ul>'


def _outcome_badge(outcome: str) -> str:
    css = f"todo-outcome todo-outcome-{esc(outcome)}"
    label = OUTCOME_LABELS.get(outcome, outcome)
    return f'<span class="{css}">{esc(label)}</span>'


def _outcome_list_html(outcomes: list[TodoOutcomeRow]) -> str:
    if not outcomes:
        return '<p class="muted">No todo items to reconcile.</p>'
    items: list[str] = []
    for row in outcomes:
        detail = ""
        if row.birth_status and row.final_status and row.birth_status != row.final_status:
            detail = (
                f' <span class="muted todo-outcome-detail">'
                f"{esc(row.birth_status)} → {esc(row.final_status)}</span>"
            )
        items.append(
            f'<li class="todo-outcome-item">'
            f"{_outcome_badge(row.outcome)}"
            f"<span>{esc(row.content)}</span>{detail}</li>"
        )
    return f'<ul class="todo-outcome-list">{"".join(items)}</ul>'


def render_todo_plan_panel(timelines: list[TodoOwnerTimeline]) -> str:
    if not timelines:
        return ""
    blocks: list[str] = []
    for timeline in timelines:
        birth_todos = todos_from_run(timeline.birth_run)
        if not birth_todos:
            continue
        rev_note = ""
        if timeline.revision_count > 2:
            rev_note = (
                f' <span class="muted">({timeline.revision_count // 2} revisions)</span>'
            )
        blocks.append(
            f"""
            <div class="todo-plan-owner">
              <h4 class="todo-plan-owner-title">{esc(timeline.owner_label)}{rev_note}</h4>
              {_todos_list_html(birth_todos, css_class="todo-list compact todo-list-full")}
            </div>
            """
        )
    if not blocks:
        return ""
    return (
        '<section class="todo-plan-panel">'
        "<h3>Plan (at birth)</h3>"
        '<p class="sub">Initial <code>write_todos</code> snapshot per agent before work proceeds.</p>'
        f'{"".join(blocks)}'
        "</section>"
    )


def render_todo_outcome_panel(timelines: list[TodoOwnerTimeline]) -> str:
    if not timelines:
        return ""
    blocks: list[str] = []
    for timeline in timelines:
        blocks.append(
            f"""
            <div class="todo-outcome-owner">
              <h4 class="todo-outcome-owner-title">{esc(timeline.owner_label)}</h4>
              {_outcome_list_html(timeline.outcomes)}
            </div>
            """
        )
    return (
        '<section class="todo-outcome-panel">'
        "<h3>Outcome (planned vs final)</h3>"
        '<p class="sub">Compares the birth plan to the last <code>write_todos</code> snapshot.</p>'
        f'{"".join(blocks)}'
        "</section>"
    )


def render_todo_plan_outcome_sections(runs: list[dict[str, Any]]) -> tuple[str, str]:
    timelines = aggregate_todo_timelines(runs)
    return render_todo_plan_panel(timelines), render_todo_outcome_panel(timelines)
