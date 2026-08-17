"""HTML fragment renderers for report pages."""

from __future__ import annotations

import html
import json
from datetime import datetime
from typing import Any, Callable
from urllib.parse import quote

from agentsmith_trace_server.models import RunEvent, RunType
from agentsmith_trace_server.report_agent_labels import (
    AgentConversationContext,
    assistant_speaker_label,
    deepagent_invoke_speaker_label,
    tool_activity_speaker_label,
    update_agent_context,
)
from agentsmith_trace_server.report_call_stack import (
    KIND_SKILL,
    KIND_SUBAGENT,
    KIND_TODOS,
    KIND_TURN_COMPLETE,
    KIND_TURN_PROMPT,
    KIND_USER_MESSAGE,
    ROLE_CLASS,
    ROLE_METHOD,
    ROLE_ROOT,
    ROLE_SKILL,
    ROLE_SKILL_REF,
    StackNode,
    activity_kind,
    build_stack_forest,
    metadata_of,
    parse_time,
    reference_label,
)
from agentsmith_trace_server.report_todos import (
    render_todo_plan_outcome_sections,
    todos_from_run,
)
from agentsmith_trace_server.report_tool_icons import (
    ICON_KIND_SKILL,
    ICON_KIND_WRITE_TODOS,
    tool_avatar_html,
    tool_bubble_label,
    tool_icon_kind,
)

ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"
ROLE_TOOL = "tool"
CHAT_ROLES = frozenset({ROLE_USER, ROLE_ASSISTANT, ROLE_SYSTEM, ROLE_TOOL})
RUN_TYPE_LLM = RunType.LLM.value
SORT_USER = 0
SORT_DEEP_INVOKE = 1
SORT_ASSISTANT = 2
SORT_TOOL = 3
HUMAN_ALIASES = {"user", "human", "humanmessage"}
ASSISTANT_ALIASES = {"assistant", "ai", "aimessage"}
SYSTEM_ALIASES = {"system", "systemmessage"}
PATH_PARAM_KEYS = ("file_path", "path", "filepath", "glob", "pattern")
AVATAR_LABELS = {
    ROLE_USER: "User",
    ROLE_ASSISTANT: "Assistant",
    ROLE_SYSTEM: "System",
    ROLE_TOOL: "Tool",
}
ICON_USER = (
    '<svg class="avatar-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm0 2c-3.31 0-6 1.79-6 4v1h12v-1c0-2.21-2.69-4-6-4Z"/>'
    "</svg>"
)
ICON_ASSISTANT = (
    '<svg class="avatar-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M9 2h6v2h5v4h-2v9a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V8H4V4h5V2Zm2 2v2h4V4h-4ZM8 8v10h8V8H8Zm-2 2h2v2H6v-2Zm12 0h2v2h-2v-2ZM10 11h1v3h-1v-3Zm5 0h1v3h-1v-3Z"/>'
    "</svg>"
)
ICON_SYSTEM = (
    '<svg class="avatar-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2Zm1 15h-2v-6h2v6Zm0-8h-2V7h2v2Z"/>'
    "</svg>"
)
ICON_TOOL = (
    '<svg class="avatar-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M22.7 19.3l-5.4-5.4c1.7-2.5 1.2-5.9-.8-7.9-2-2-5.4-2.5-7.9-.8l-5.4-5.4c-.4-.4-1-.4-1.4 0l-1.4 1.4c-.4.4-.4 1 0 1.4l5.4 5.4c-1.7 2.5-1.2 5.9.8 7.9 2 2 5.4 2.5 7.9.8l5.4 5.4c.4.4 1 .4 1.4 0l1.4-1.4c.4-.4.4-1 0-1.4ZM9.5 11.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3Z"/>'
    "</svg>"
)
AVATAR_ICONS = {
    ROLE_USER: ICON_USER,
    ROLE_ASSISTANT: ICON_ASSISTANT,
    ROLE_SYSTEM: ICON_SYSTEM,
    ROLE_TOOL: ICON_TOOL,
}
PILL_BY_ROLE = {
    ROLE_ROOT: "deep-agent",
    ROLE_CLASS: "class",
    ROLE_SKILL: "skill",
    ROLE_SKILL_REF: "ref",
    ROLE_METHOD: "method",
}
STACK_TITLE_PREFIX = {
    ROLE_ROOT: "",
    ROLE_CLASS: "",
    ROLE_SKILL: "",
    ROLE_SKILL_REF: "",
    ROLE_METHOD: "",
}
STACK_ROLE_EMOJI = {
    ROLE_ROOT: "🤖",
    ROLE_CLASS: "🐜",
    ROLE_SKILL: "🛠️",
    ROLE_SKILL_REF: "🛠️",
}
STACK_PILL_LABEL = {
    ROLE_ROOT: "deep-agent",
    ROLE_CLASS: "sub-agent",
    ROLE_SKILL: "skill",
    ROLE_SKILL_REF: "ref",
}
TOOLTIP_MIN_LEN = 36
CONTENT_PREVIEW_FIRST_MAX = 88
CONTENT_PREVIEW_END_MAX = 88
CONTENT_PREVIEW_MIN_SPLIT = 120


def esc(value: Any) -> str:
    return html.escape(str(value))


def _normalize_preview_text(text: str) -> str:
    return " ".join(str(text or "").split())


def _two_line_ellipsis(
    text: str,
    *,
    first_max: int = CONTENT_PREVIEW_FIRST_MAX,
    end_max: int = CONTENT_PREVIEW_END_MAX,
    min_split: int = CONTENT_PREVIEW_MIN_SPLIT,
) -> str:
    ## ⬇️ Line 1: beginning + "..."; line 2: "..." + ending (middle omitted)
    cleaned = _normalize_preview_text(text)
    if len(cleaned) <= min_split:
        return cleaned
    head = cleaned[:first_max].rstrip()
    tail = cleaned[-end_max:].lstrip()
    if not head or not tail:
        return cleaned[: min_split - 1] + "..."
    return f"{head}...\n...{tail}"


def _pre_content_html(text: str) -> str:
    full = str(text or "")
    tip_cls, tip_attr = _tip_attrs(full, min_len=CONTENT_PREVIEW_MIN_SPLIT)
    return f'<pre class="content{tip_cls}"{tip_attr}>{esc(full)}</pre>'


def format_content(content: Any) -> str:
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            elif isinstance(block, dict):
                parts.append(json.dumps(block, ensure_ascii=False))
            else:
                parts.append(str(block))
        if parts:
            return "\n".join(parts)
        return json.dumps(content, ensure_ascii=False, indent=2)
    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False, indent=2)
    return str(content)


def render_messages(messages: list[dict[str, Any]] | Any) -> str:
    if not isinstance(messages, list) or not messages:
        return "<em>No messages</em>"
    blocks: list[str] = []
    for msg in messages:
        role = esc(msg.get("role", msg.get("type", "unknown")))
        content_text = _pre_content_html(format_content(msg.get("content", "")))
        blocks.append(
            f'<div class="msg"><div class="role">{role}</div>'
            f'{content_text}</div>'
        )
    return "".join(blocks)


def render_outputs(outputs: dict[str, Any]) -> str:
    if not outputs:
        return "<em>No output</em>"
    sections: list[str] = []
    content = outputs.get("content")
    if content not in (None, ""):
        sections.append(
            f"<h4>Content</h4>{_pre_content_html(format_content(content))}"
        )
    tool_calls = outputs.get("tool_calls")
    if tool_calls:
        sections.append(
            f"<h4>Tool calls</h4><pre class=\"content\">"
            f"{esc(json.dumps(tool_calls, ensure_ascii=False, indent=2))}</pre>"
        )
    if outputs.get("error"):
        sections.append(
            f"<h4>Error</h4><pre class=\"content\">{esc(outputs['error'])}</pre>"
        )
    token_usage = outputs.get("token_usage")
    if token_usage:
        sections.append(
            f"<h4>Token usage</h4><pre class=\"content\">"
            f"{esc(json.dumps(token_usage, ensure_ascii=False, indent=2))}</pre>"
        )
    if not sections:
        sections.append(
            f"<pre class=\"content\">{esc(json.dumps(outputs, ensure_ascii=False, indent=2))}</pre>"
        )
    return "".join(sections)


def render_metadata(metadata: dict[str, Any]) -> str:
    if not metadata:
        return "<em>No metadata</em>"
    items: list[str] = []
    for key in sorted(metadata):
        value = metadata[key]
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, ensure_ascii=False)
        else:
            rendered = str(value)
        items.append(f"<dt>{esc(key)}</dt><dd><code>{esc(rendered)}</code></dd>")
    return f'<dl class="meta-grid">{"".join(items)}</dl>'


def indent_level(run: dict[str, Any], runs_by_id: dict[str, dict[str, Any]]) -> int:
    depth = 0
    parent_id = run.get("parent_run_id")
    seen: set[str] = set()
    while parent_id and parent_id not in seen:
        seen.add(str(parent_id))
        depth += 1
        parent = runs_by_id.get(str(parent_id))
        if not parent:
            break
        parent_id = parent.get("parent_run_id")
    return depth


def run_to_dict(run: RunEvent | dict[str, Any]) -> dict[str, Any]:
    if isinstance(run, RunEvent):
        return run.model_dump(mode="json")
    return run


def _render_raw_inputs_html(inputs_json: dict[str, Any]) -> str:
    extra_keys = set(inputs_json.keys()) - {"messages", "todos"}
    if not extra_keys:
        return ""
    payload = dict(inputs_json)
    payload.pop("todos", None)
    if extra_keys == {"content"} and isinstance(payload.get("content"), str):
        return f"<h4>Raw inputs</h4>{_pre_content_html(payload['content'])}"
    if extra_keys == {"args"} and isinstance(payload.get("args"), dict):
        args_copy = dict(payload["args"])
        if isinstance(args_copy.get("todos"), list):
            args_copy = {k: v for k, v in args_copy.items() if k != "todos"}
        if not args_copy:
            return ""
        payload["args"] = args_copy
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    return f"<h4>Raw inputs</h4>{_pre_content_html(rendered)}"


def render_run_panel(
    run: dict[str, Any],
    *,
    detail_url: str | None = None,
    show_detail_link: bool = True,
) -> str:
    run_id = str(run.get("run_id", ""))
    messages = run.get("inputs", {}).get("messages", [])
    inputs_json = run.get("inputs", {})
    outputs = run.get("outputs", {})
    metadata = run.get("metadata", {})
    detail_link = _detail_link(run_id, detail_url, show_detail_link)
    todos_block = ""
    todos_html = _todos_list_html(run)
    if todos_html:
        todos_block = f"<h4>Todo list</h4>{todos_html}"
    inputs_extra = ""
    if inputs_json and (not messages or set(inputs_json.keys()) - {"messages", "todos"}):
        inputs_extra = _render_raw_inputs_html(inputs_json)
    return f"""
    <div class="panel">
      <h4>Input messages</h4>
      {render_messages(messages)}
      {todos_block}
      {inputs_extra}
      <h4>Output</h4>
      {render_outputs(outputs)}
      <h4>Metadata</h4>
      {render_metadata(metadata)}
      {detail_link}
    </div>
    """


def _stack_display_name(node: StackNode) -> str:
    run = node.run
    meta = metadata_of(run)
    if node.role == ROLE_ROOT:
        for key in ("deepagent", "agent_name"):
            val = meta.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        name = run.get("name")
        if isinstance(name, str) and name.strip() and name.strip() != "turn_prompt":
            return name.strip()
        return "deep-agent"
    if node.role == ROLE_SKILL_REF:
        return reference_label(run)
    if node.role == ROLE_SKILL:
        skill_id = meta.get("skill_id")
        if isinstance(skill_id, str) and skill_id.strip():
            return skill_id.strip()
    if node.role == ROLE_CLASS:
        name = run.get("name") or meta.get("subagent_type") or activity_kind(run)
        return str(name)
    return str(run.get("name") or run.get("run_type") or "run")


def _stack_pill_html(role: str) -> str:
    emoji = STACK_ROLE_EMOJI.get(role, "")
    label = STACK_PILL_LABEL.get(role) or PILL_BY_ROLE.get(role, "method")
    emoji_html = (
        f'<span class="pill-emoji" aria-hidden="true">{emoji}</span> '
        if emoji
        else ""
    )
    return f'<span class="pill pill-{esc(PILL_BY_ROLE.get(role, "method"))}">{emoji_html}{esc(label)}</span>'


def _render_stack_node(
    node: StackNode,
    *,
    open_run_id: str | None,
    detail_url_builder: Callable[[str], str] | None,
    anchor_time: datetime | None,
    thread_finished: bool,
) -> str:
    run = node.run
    run_id = str(run.get("run_id", ""))
    open_attr = " open" if open_run_id and run_id == open_run_id else ""
    detail_url = detail_url_builder(run_id) if detail_url_builder else None
    panel = render_run_panel(run, detail_url=detail_url)
    role = node.role
    prefix = STACK_TITLE_PREFIX.get(role, "")
    title = _stack_display_name(node)
    title_full = f"{prefix}{title}"
    title_tip_cls, title_tip_attr = _tip_attrs(title_full, min_len=24)
    pill_html = _stack_pill_html(role)
    param = _run_param_text(run)
    param_row = _stack_param_row_html(param) if param else ""
    todos_row = ""
    if activity_kind(run) == KIND_TODOS or tool_icon_kind(run) == ICON_KIND_WRITE_TODOS:
        todos_html = _todos_list_html(run)
        if todos_html:
            todos_row = f'<div class="stack-summary-todos">{todos_html}</div>'
    time_label = _format_event_time(run.get("start_time"), anchor_time) or ""
    status_html = _status_merge_html(run, thread_finished=thread_finished)
    kids = "".join(
        _render_stack_node(
            child,
            open_run_id=open_run_id,
            detail_url_builder=detail_url_builder,
            anchor_time=anchor_time,
            thread_finished=thread_finished,
        )
        for child in node.children
    )
    child_block = f'<ul class="call-stack">{kids}</ul>' if kids else ""
    return f"""
    <li class="stack-node stack-{esc(role)}">
      <details class="run stack-frame" id="run-{html.escape(run_id)}"{open_attr}>
        <summary class="stack-summary">
          <div class="stack-summary-row stack-summary-head">
            <span class="stack-summary-leading">
              {pill_html}
              <strong class="stack-title{title_tip_cls}"{title_tip_attr}>{esc(prefix)}{esc(title)}</strong>
            </span>
            <span class="stack-summary-end">
              {status_html}
              <span class="stack-time muted">{esc(time_label)}</span>
              <span class="muted stack-run-id"><code>{esc(run_id[:12])}…</code></span>
            </span>
          </div>
          {param_row}
          {todos_row}
        </summary>
        {panel}
      </details>
      {child_block}
    </li>
    """


def render_runs_list(
    runs: list[RunEvent | dict[str, Any]],
    *,
    open_run_id: str | None = None,
    detail_url_builder: Callable[[str], str] | None = None,
) -> str:
    if not runs:
        return "<p class='muted'>暂无记录。</p>"
    dict_runs = [run_to_dict(run) for run in runs]
    plan_html, outcome_html = render_todo_plan_outcome_sections(dict_runs)
    forest = build_stack_forest(dict_runs)
    anchor_time = _thread_anchor_time(dict_runs)
    thread_finished = _thread_turn_finished(dict_runs)
    items = "".join(
        _render_stack_node(
            node,
            open_run_id=open_run_id,
            detail_url_builder=detail_url_builder,
            anchor_time=anchor_time,
            thread_finished=thread_finished,
        )
        for node in forest
    )
    stack_body = (
        '<p class="sub stack-legend">调用栈：🤖 DeepAgent 为根；🐜 SubAgent；'
        "LLM/工具为 method；🛠️ 技能与 references 单独标记。</p>"
        f'<ul class="call-stack call-stack-root">{items}</ul>'
    )
    parts: list[str] = []
    if plan_html:
        parts.append(plan_html)
    parts.append(stack_body)
    if outcome_html:
        parts.append(outcome_html)
    return "".join(parts)


def _thread_has_user_message(runs: list[RunEvent | dict[str, Any]]) -> bool:
    for run in runs:
        data = run if isinstance(run, dict) else run_to_dict(run)
        if activity_kind(data) == KIND_USER_MESSAGE:
            return True
    return False


def render_conversation(runs: list[RunEvent | dict[str, Any]]) -> str:
    """Chat-style transcript derived from LLM runs, with activity chips for other runs."""
    if not runs:
        return '<div class="empty">该线程暂无运行记录。</div>'
    dict_runs = [run_to_dict(run) for run in runs]
    anchor_time = _thread_anchor_time(dict_runs)
    thread_finished = _thread_turn_finished(dict_runs)
    items: list[tuple[int, str, str]] = []
    ctx = AgentConversationContext()
    seen_users: set[str] = set()
    include_user_from_llm = not _thread_has_user_message(runs)
    for data in _conversation_runs(runs):
        update_agent_context(ctx, data)
        sort_time = str(data.get("start_time") or "")
        activity = activity_kind(data)
        if activity == KIND_TURN_COMPLETE:
            continue
        if activity == KIND_USER_MESSAGE:
            text = _user_message_text(data)
            if text and text not in seen_users:
                seen_users.add(text)
                items.append(
                    (
                        SORT_USER,
                        sort_time,
                        _bubble(
                            ROLE_USER,
                            text,
                            label="User",
                            start_time=data.get("start_time"),
                            anchor_time=anchor_time,
                        ),
                    )
                )
            continue
        if activity == KIND_TURN_PROMPT:
            items.append(
                (
                    SORT_DEEP_INVOKE,
                    sort_time,
                    _deepagent_invoke_chip(data, ctx, anchor_time=anchor_time),
                )
            )
            continue
        run_type = str(data.get("run_type") or "")
        if run_type == RUN_TYPE_LLM:
            for sort_group, html in _llm_bubble_items(
                data,
                ctx,
                seen_users,
                include_user=include_user_from_llm,
                anchor_time=anchor_time,
            ):
                items.append((sort_group, sort_time, html))
            continue
        items.append(
            (SORT_TOOL, sort_time, _activity_chip(data, ctx, anchor_time=anchor_time, thread_finished=thread_finished))
        )
    items.sort(key=lambda row: (row[0], row[1]))
    parts: list[str] = [
        '<div class="chat-panel">',
        '<div class="chat-toolbar">',
        '<button type="button" data-chat-expand-all>Expand all</button>',
        '<button type="button" data-chat-collapse-all>Collapse all</button>',
        "</div>",
        '<div class="chat">',
    ]
    parts.extend(html for _, _, html in items)
    parts.append("</div></div>")
    return "".join(parts)


def _user_message_text(run: dict[str, Any]) -> str:
    inputs = run.get("inputs")
    if not isinstance(inputs, dict):
        return ""
    for key in ("content", "human_preview", "text"):
        raw = inputs.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return ""


def _deepagent_invoke_chip(
    run: dict[str, Any],
    ctx: AgentConversationContext,
    *,
    anchor_time: datetime | None = None,
) -> str:
    speaker = deepagent_invoke_speaker_label(run, ctx)
    inner = _compact_bubble_body(
        speaker,
        "invoked",
        meta=_format_event_time(run.get("start_time"), anchor_time),
    )
    return _chat_row(
        ROLE_ASSISTANT,
        inner,
        bubble_class="assistant deepagent-invoke",
    )


def _normalize_path_key(path: str) -> str:
    return path.strip().replace("\\", "/").lower()


def _tool_identity_key(run: dict[str, Any]) -> tuple[str, str]:
    meta = metadata_of(run)
    tool = str(meta.get("tool_name") or run.get("name") or "").strip().lower()
    path = _normalize_path_key(_extract_tool_target_path(run) or "")
    return tool, path


def _skill_shadow_keys(run: dict[str, Any]) -> set[tuple[str, str]]:
    if activity_kind(run) != KIND_SKILL:
        return set()
    tool, path = _tool_identity_key(run)
    if not tool:
        return set()
    return {(tool, path)}


def _collect_skill_shadow_keys(runs: list[dict[str, Any]]) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for run in runs:
        keys.update(_skill_shadow_keys(run))
    return keys


def _is_shadowed_tool_run(run: dict[str, Any], shadow_keys: set[tuple[str, str]]) -> bool:
    ## ⬇️ LangChain tool callback + SEAI skill_used for the same invocation — show skill row only
    if activity_kind(run) == KIND_SKILL:
        return False
    if str(run.get("run_type") or "") != RunType.TOOL.value:
        return False
    key = _tool_identity_key(run)
    if not key[0]:
        return False
    return key in shadow_keys


def _conversation_runs(runs: list[RunEvent | dict[str, Any]]) -> list[dict[str, Any]]:
    dict_runs = [run_to_dict(run) for run in runs]
    shadow_keys = _collect_skill_shadow_keys(dict_runs)
    if not shadow_keys:
        return dict_runs
    return [run for run in dict_runs if not _is_shadowed_tool_run(run, shadow_keys)]


def report_home_href(
    *,
    thread_id: str | None = None,
    user_id: str | None = None,
    run_id: str | None = None,
) -> str:
    params: list[str] = []
    if user_id:
        params.append(f"user_id={quote(user_id, safe='')}")
    if thread_id:
        params.append(f"thread_id={quote(thread_id, safe='')}")
    if run_id:
        params.append(f"run_id={quote(run_id, safe='')}")
    if not params:
        return "/report"
    return "/report?" + "&".join(params)


def _detail_link(run_id: str, detail_url: str | None, show: bool) -> str:
    if not show:
        return ""
    href = detail_url or (f"/report/runs/{esc(run_id)}" if run_id else "")
    if not href:
        return ""
    return f'<div class="actions"><a href="{esc(href)}">Open full run detail</a></div>'


def _normalize_role(raw: Any) -> str:
    text = str(raw or "").strip().lower()
    if text in HUMAN_ALIASES:
        return ROLE_USER
    if text in ASSISTANT_ALIASES:
        return ROLE_ASSISTANT
    if text in SYSTEM_ALIASES:
        return ROLE_SYSTEM
    return text or "unknown"


def _avatar(role: str) -> str:
    row_role = role if role in CHAT_ROLES else ROLE_ASSISTANT
    label = AVATAR_LABELS.get(row_role, "Message")
    icon = AVATAR_ICONS.get(row_role, ICON_ASSISTANT)
    return (
        f'<div class="chat-avatar chat-avatar-{esc(row_role)}" aria-label="{esc(label)}">'
        f"{icon}</div>"
    )


def _thread_anchor_time(runs: list[dict[str, Any]]) -> datetime | None:
    times = [parse_time(r.get("start_time")) for r in runs]
    valid = [t for t in times if t is not None]
    return min(valid) if valid else None


def _format_event_time(value: Any, anchor: datetime | None) -> str | None:
    """First event shows wall-clock time; later events show +seconds from anchor."""
    when = parse_time(value)
    if when is None:
        return None
    if anchor is None:
        return _format_run_time(value)
    delta = (when - anchor).total_seconds()
    if abs(delta) < 0.05:
        return _format_run_time(value)
    if delta < 0:
        return _format_run_time(value)
    return f"+{delta:.2f}s"


def _truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _llm_stack_detail(run: dict[str, Any], *, max_len: int = 240) -> str | None:
    if str(run.get("run_type") or "").lower() != RUN_TYPE_LLM:
        return None
    outputs = run.get("outputs") if isinstance(run.get("outputs"), dict) else {}
    content = str(outputs.get("content") or "").strip()
    if content:
        return _truncate_text(content, max_len)
    tool_calls = outputs.get("tool_calls")
    if isinstance(tool_calls, list) and tool_calls:
        parts: list[str] = []
        for tc in tool_calls:
            if not isinstance(tc, dict):
                continue
            name = str(tc.get("name") or "tool").strip()
            args = tc.get("args") if isinstance(tc.get("args"), dict) else {}
            suffix = ""
            if name == "task":
                sub = args.get("subagent_type")
                if isinstance(sub, str) and sub.strip():
                    suffix = f" → {sub.strip()}"
            else:
                for key in ("file_path", "path", "command"):
                    val = args.get(key)
                    if isinstance(val, str) and val.strip():
                        suffix = f" → {val.strip()}"
                        break
            parts.append(f"{name}{suffix}")
        if parts:
            return _truncate_text("calls: " + ", ".join(parts), max_len)
    usage = outputs.get("token_usage")
    if isinstance(usage, dict) and usage.get("total_tokens") is not None:
        return f"tokens: {usage['total_tokens']}"
    return None


def _run_param_text(run: dict[str, Any], *, max_len: int = 240) -> str | None:
    user_text = _user_message_text(run)
    if user_text:
        return _prose_stack_preview(user_text)
    llm_detail = _llm_stack_detail(run, max_len=max_len)
    if llm_detail:
        return llm_detail
    path = _extract_tool_target_path(run)
    if path:
        return _truncate_text(path.strip(), max_len)
    meta = metadata_of(run)
    inputs = run.get("inputs") if isinstance(run.get("inputs"), dict) else {}
    if activity_kind(run) == KIND_SUBAGENT:
        for key in ("description", "task_description"):
            val = meta.get(key) or inputs.get(key)
            if isinstance(val, str) and val.strip():
                return _prose_stack_preview(val.strip())
    for key in ("command", "cmd", "description", "task_description"):
        val = meta.get(key) or inputs.get(key)
        if isinstance(val, str) and val.strip():
            return _prose_stack_preview(val.strip())
    preview = meta.get("args_preview")
    if isinstance(preview, str) and preview.strip():
        return _truncate_text(preview.strip(), max_len)
    return None


def _param_code_html(text: str, *, css_class: str = "bubble-param") -> str:
    tip_cls, tip_attr = _tip_attrs(text, min_len=1)
    return (
        f'<code class="{esc(css_class)}{tip_cls}"{tip_attr}>{esc(text)}</code>'
    )


def _stack_param_row_html(text: str) -> str:
    multiline = "\n" in text
    multi_cls = " stack-param-multiline" if multiline else ""
    tip_cls, tip_attr = _tip_attrs(text, min_len=1)
    return (
        f'<div class="stack-summary-row stack-summary-param">'
        f'<span class="stack-param-line{multi_cls}{tip_cls}"{tip_attr}>{esc(text)}</span>'
        "</div>"
    )


def _tip_attrs(text: str, *, min_len: int = TOOLTIP_MIN_LEN) -> tuple[str, str]:
    cleaned = str(text or "").strip()
    if len(cleaned) < min_len:
        return "", ""
    return " has-tip", f' title="{esc(cleaned)}"'


def _status_pill(label: str, css: str, tip: str | None = None) -> str:
    tip_attr = f' title="{esc(tip)}"' if tip else ""
    extra = " has-tip" if tip else ""
    return (
        f'<span class="status-pill status-{css}{extra}"{tip_attr}>{esc(label)}</span>'
    )


def _thread_turn_finished(runs: list[dict[str, Any]]) -> bool:
    for run in runs:
        if activity_kind(run) == KIND_TURN_COMPLETE:
            return True
    return False


def _status_merge_html(run: dict[str, Any], *, thread_finished: bool = False) -> str:
    """Inline pending → success/error pills; tooltip describes the lifecycle."""
    status = str(run.get("status") or "unknown").strip().lower()
    meta = metadata_of(run)
    end_time = run.get("end_time")
    has_end = end_time is not None and str(end_time).strip()
    outputs = run.get("outputs") if isinstance(run.get("outputs"), dict) else {}
    duration = meta.get("duration_ms") or outputs.get("duration_ms")

    if status == "pending" and not has_end:
        if thread_finished:
            tip = (
                "Turn finished — this step completed; "
                "trace did not record a separate completion event"
            )
            return (
                f'<span class="status-merge has-tip" title="{esc(tip)}">'
                f'{_status_pill("pending", "pending")}'
                '<span class="status-merge-arrow" aria-hidden="true">→</span>'
                f'{_status_pill("success", "success")}'
                "</span>"
            )
        return _status_pill(
            "pending",
            "pending",
            "Still running — wait until the turn finishes",
        )

    if status == "success":
        tip_parts = ["pending → success"]
        if duration is not None:
            tip_parts.append(f"{duration} ms")
        elif has_end:
            tip_parts.append("completed")
        tip = " · ".join(tip_parts)
        return (
            f'<span class="status-merge has-tip" title="{esc(tip)}">'
            f'{_status_pill("pending", "pending")}'
            '<span class="status-merge-arrow" aria-hidden="true">→</span>'
            f'{_status_pill("success", "success")}'
            "</span>"
        )

    if status == "error":
        err = outputs.get("error") or meta.get("error") or "failed"
        tip = f"pending → error · {err}"
        return (
            f'<span class="status-merge has-tip" title="{esc(str(tip))}">'
            f'{_status_pill("pending", "pending")}'
            '<span class="status-merge-arrow" aria-hidden="true">→</span>'
            f'{_status_pill("error", "error")}'
            "</span>"
        )

    return _status_pill(status, status, status)


def _format_run_time(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if "T" in text:
        date_part, time_part = text.split("T", 1)
        time_part = time_part.replace("Z", "").split("+")[0].split(".")[0]
        return f"{date_part} {time_part}"
    return text


def _prose_stack_preview(text: str) -> str:
    return _two_line_ellipsis(text)


def _compact_bubble_body(
    speaker: str,
    text: str,
    *,
    param: str | None = None,
    meta: str | None = None,
    extra_html: str = "",
    status_html: str = "",
) -> str:
    text_tip_cls, text_tip_attr = _tip_attrs(text, min_len=CONTENT_PREVIEW_MIN_SPLIT)
    preview = _two_line_ellipsis(text)
    if preview == text:
        text_html = (
            f'<span class="bubble-text{text_tip_cls}"{text_tip_attr}>{esc(text)}</span>'
        )
    else:
        text_html = (
            f'<span class="bubble-text bubble-text-preview{text_tip_cls}"{text_tip_attr}>'
            f'{esc(preview)}</span>'
            f'<span class="bubble-text bubble-text-full">{esc(text)}</span>'
        )
    main_parts = [
        f'<span class="speaker">{esc(speaker)}</span>',
        text_html,
    ]
    if status_html:
        main_parts.append(status_html)
    if param:
        main_parts.append(_param_code_html(param))
    main = f'<div class="bubble-main">{"".join(main_parts)}</div>'
    meta_html = f'<div class="bubble-meta">{esc(meta)}</div>' if meta else ""
    extra_block = f'<div class="bubble-todos">{extra_html}</div>' if extra_html else ""
    return f"{main}{extra_block}{meta_html}"


def _chat_row(
    role: str,
    bubble_inner: str,
    *,
    avatar_html: str | None = None,
    bubble_class: str | None = None,
) -> str:
    row_role = role if role in CHAT_ROLES else ROLE_ASSISTANT
    css = bubble_class or row_role
    bubble = (
        f'<div class="bubble compact bubble-expandable {esc(css)}" '
        f'role="button" tabindex="0">{bubble_inner}</div>'
    )
    avatar = avatar_html if avatar_html else _avatar(row_role)
    row_class = f"chat-row-{row_role}"
    if row_role == ROLE_USER:
        block = f'<div class="chat-block">{bubble}{avatar}</div>'
    else:
        block = f'<div class="chat-block">{avatar}{bubble}</div>'
    return f'<div class="chat-row {row_class}">{block}</div>'


def _bubble(
    role: str,
    body: str,
    *,
    label: str | None = None,
    start_time: Any = None,
    anchor_time: datetime | None = None,
) -> str:
    css = role if role in {ROLE_USER, ROLE_ASSISTANT, ROLE_SYSTEM} else ROLE_ASSISTANT
    speaker = label or css
    inner = _compact_bubble_body(
        speaker,
        body,
        meta=_format_event_time(start_time, anchor_time),
    )
    return _chat_row(css, inner)


def _llm_bubble_items(
    run: dict[str, Any],
    ctx: AgentConversationContext,
    seen_users: set[str],
    *,
    include_user: bool = True,
    anchor_time: datetime | None = None,
) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    messages = run.get("inputs", {}).get("messages", [])
    last_user: str | None = None
    if include_user and isinstance(messages, list):
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            role = _normalize_role(msg.get("role", msg.get("type")))
            text = format_content(msg.get("content", "")).strip()
            if role == ROLE_USER and text:
                last_user = text
    if last_user and last_user not in seen_users:
        seen_users.add(last_user)
        out.append(
            (
                SORT_USER,
                _bubble(
                    ROLE_USER,
                    last_user,
                    label="User",
                    start_time=run.get("start_time"),
                    anchor_time=anchor_time,
                ),
            )
        )
    content = run.get("outputs", {}).get("content")
    if content not in (None, ""):
        speaker = assistant_speaker_label(run, ctx)
        out.append(
            (
                SORT_ASSISTANT,
                _bubble(
                    ROLE_ASSISTANT,
                    format_content(content),
                    label=speaker,
                    start_time=run.get("start_time"),
                    anchor_time=anchor_time,
                ),
            )
        )
    error = run.get("outputs", {}).get("error")
    if error:
        speaker = assistant_speaker_label(run, ctx)
        out.append(
            (
                SORT_ASSISTANT,
                _bubble(
                    ROLE_ASSISTANT,
                    f"Error: {error}",
                    label=speaker,
                    start_time=run.get("start_time"),
                    anchor_time=anchor_time,
                ),
            )
        )
    return out


def _llm_bubbles(run: dict[str, Any], ctx: AgentConversationContext) -> list[str]:
    seen: set[str] = set()
    return [html for _, html in _llm_bubble_items(run, ctx, seen)]


def _path_from_dict(data: dict[str, Any]) -> str | None:
    for key in PATH_PARAM_KEYS:
        raw = data.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return None


def _path_from_args_preview(preview: str) -> str | None:
    text = preview.strip()
    if not text:
        return None
    for key in PATH_PARAM_KEYS:
        for quote in ("'", '"'):
            needle = f"{quote}{key}{quote}: {quote}"
            idx = text.find(needle)
            if idx < 0:
                continue
            start = idx + len(needle)
            end = text.find(quote, start)
            if end > start:
                return text[start:end]
    return None


def _format_tool_target_display(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    parts = [part for part in normalized.split("/") if part and part != "."]
    if not parts:
        return path.strip()
    if len(parts) == 1:
        return parts[-1]
    return f"{parts[-2]}/{parts[-1]}"


def _extract_tool_target_path(run: dict[str, Any]) -> str | None:
    inputs = run.get("inputs")
    meta = run.get("metadata")
    inputs_dict = inputs if isinstance(inputs, dict) else {}
    meta_dict = meta if isinstance(meta, dict) else {}

    path = _path_from_dict(inputs_dict)
    if path:
        return path

    payload = inputs_dict.get("payload")
    if isinstance(payload, dict):
        path = _path_from_dict(payload)
        if path:
            return path

    path = _path_from_dict(meta_dict)
    if path:
        return path

    preview = meta_dict.get("args_preview")
    if isinstance(preview, str):
        return _path_from_args_preview(preview)

    return None


def _tool_target_detail(run: dict[str, Any]) -> str | None:
    path = _extract_tool_target_path(run)
    if not path:
        return None
    return path.strip()


def _todos_from_run(run: dict[str, Any]) -> list[dict[str, Any]]:
    return todos_from_run(run)


def _todos_list_html(run: dict[str, Any]) -> str:
    todos = _todos_from_run(run)
    if not todos:
        return ""
    items: list[str] = []
    for todo in todos:
        content = str(todo.get("content") or "").strip()
        if not content:
            continue
        status = str(todo.get("status") or "").strip()
        status_html = (
            f'<span class="todo-status">{esc(status)}</span>' if status else ""
        )
        items.append(f'<li class="todo-item">{status_html}<span>{esc(content)}</span></li>')
    if not items:
        return ""
    return f'<ul class="todo-list compact todo-list-full">{"".join(items)}</ul>'


def _activity_chip(
    run: dict[str, Any],
    ctx: AgentConversationContext,
    *,
    anchor_time: datetime | None = None,
    thread_finished: bool = False,
) -> str:
    meta = run.get("metadata") or {}
    if not isinstance(meta, dict):
        meta = {}
    icon_kind = tool_icon_kind(run)
    tool_name = str(meta.get("tool_name") or run.get("name") or "").strip()
    skill_id = str(meta.get("skill_id") or "").strip()
    kind = esc(run.get("run_type", "run"))
    activity = meta.get("activity_kind")
    extra = ""
    if activity and str(activity) != KIND_SKILL:
        extra = f" · {esc(activity)}"
    tool_label = tool_bubble_label(icon_kind)
    speaker = tool_activity_speaker_label(run, ctx, tool_label)
    if icon_kind == ICON_KIND_SKILL:
        label_parts: list[str] = []
        if skill_id:
            label_parts.append(skill_id)
        if tool_name and tool_name != skill_id:
            label_parts.append(tool_name)
        display_name = esc(" · ".join(label_parts) if label_parts else tool_name or "skill")
    else:
        display_name = esc(tool_name or str(run.get("name") or "tool"))
    summary = f"{kind}: {display_name}{extra}"
    target = _tool_target_detail(run)
    todos_html = ""
    if icon_kind == ICON_KIND_WRITE_TODOS:
        todos_html = _todos_list_html(run)
    inner = _compact_bubble_body(
        speaker,
        summary,
        param=target,
        meta=_format_event_time(run.get("start_time"), anchor_time),
        extra_html=todos_html,
        status_html=_status_merge_html(run, thread_finished=thread_finished),
    )
    bubble_class = f"{ROLE_TOOL} {icon_kind}"
    return _chat_row(
        ROLE_TOOL,
        inner,
        avatar_html=tool_avatar_html(icon_kind),
        bubble_class=bubble_class,
    )
