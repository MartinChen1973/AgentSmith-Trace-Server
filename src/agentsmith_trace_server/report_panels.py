"""HTML fragment renderers for report pages."""

from __future__ import annotations

import html
import json
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
    reference_label,
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
    ROLE_CLASS: "class ",
    ROLE_SKILL: "skill ",
    ROLE_SKILL_REF: "ref ",
    ROLE_METHOD: "",
}


def esc(value: Any) -> str:
    return html.escape(str(value))


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
        content_text = esc(format_content(msg.get("content", "")))
        blocks.append(
            f'<div class="msg"><div class="role">{role}</div>'
            f'<pre class="content">{content_text}</pre></div>'
        )
    return "".join(blocks)


def render_outputs(outputs: dict[str, Any]) -> str:
    if not outputs:
        return "<em>No output</em>"
    sections: list[str] = []
    content = outputs.get("content")
    if content not in (None, ""):
        sections.append(
            f"<h4>Content</h4><pre class=\"content\">{esc(format_content(content))}</pre>"
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
    inputs_extra = ""
    if inputs_json and (not messages or set(inputs_json.keys()) - {"messages"}):
        inputs_extra = (
            f"<h4>Raw inputs</h4>"
            f"<pre class=\"content\">{esc(json.dumps(inputs_json, ensure_ascii=False, indent=2))}</pre>"
        )
    return f"""
    <div class="panel">
      <h4>Input messages</h4>
      {render_messages(messages)}
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
    if node.role == ROLE_SKILL_REF:
        return reference_label(run)
    if node.role == ROLE_SKILL:
        skill_id = metadata_of(run).get("skill_id")
        if isinstance(skill_id, str) and skill_id.strip():
            return skill_id.strip()
    if node.role == ROLE_CLASS:
        name = run.get("name") or activity_kind(run)
        return str(name)
    return str(run.get("name") or run.get("run_type") or "run")


def _render_stack_node(
    node: StackNode,
    *,
    open_run_id: str | None,
    detail_url_builder: Callable[[str], str] | None,
) -> str:
    run = node.run
    run_id = str(run.get("run_id", ""))
    open_attr = " open" if open_run_id and run_id == open_run_id else ""
    detail_url = detail_url_builder(run_id) if detail_url_builder else None
    panel = render_run_panel(run, detail_url=detail_url)
    role = node.role
    pill = PILL_BY_ROLE.get(role, "method")
    prefix = STACK_TITLE_PREFIX.get(role, "")
    title = _stack_display_name(node)
    kids = "".join(
        _render_stack_node(
            child,
            open_run_id=open_run_id,
            detail_url_builder=detail_url_builder,
        )
        for child in node.children
    )
    child_block = f'<ul class="call-stack">{kids}</ul>' if kids else ""
    return f"""
    <li class="stack-node stack-{esc(role)}">
      <details class="run stack-frame" id="run-{html.escape(run_id)}"{open_attr}>
        <summary>
          <span class="pill pill-{esc(pill)}">{esc(pill)}</span>
          <strong class="stack-title">{esc(prefix)}{esc(title)}</strong>
          <span class="muted">{esc(run.get('status', ''))}</span>
          <span class="muted">{esc(run.get('start_time', ''))}</span>
          <span class="muted"><code>{esc(run_id[:8])}…</code></span>
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
    forest = build_stack_forest(dict_runs)
    items = "".join(
        _render_stack_node(
            node,
            open_run_id=open_run_id,
            detail_url_builder=detail_url_builder,
        )
        for node in forest
    )
    return (
        '<p class="sub stack-legend">调用栈：DeepAgent 为根；SubAgent 为 class；'
        "LLM/工具为 method；技能与 references 单独标记。</p>"
        f'<ul class="call-stack call-stack-root">{items}</ul>'
    )


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
                        ),
                    )
                )
            continue
        if activity == KIND_TURN_PROMPT:
            items.append(
                (
                    SORT_DEEP_INVOKE,
                    sort_time,
                    _deepagent_invoke_chip(data, ctx),
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
            ):
                items.append((sort_group, sort_time, html))
            continue
        items.append((SORT_TOOL, sort_time, _activity_chip(data, ctx)))
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


def _deepagent_invoke_chip(run: dict[str, Any], ctx: AgentConversationContext) -> str:
    speaker = deepagent_invoke_speaker_label(run, ctx)
    inner = _compact_bubble_body(
        speaker,
        "invoked",
        meta=_format_run_time(run.get("start_time")),
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


def _format_run_time(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if "T" in text:
        date_part, time_part = text.split("T", 1)
        time_part = time_part.replace("Z", "").split("+")[0].split(".")[0]
        return f"{date_part} {time_part}"
    return text


def _compact_bubble_body(
    speaker: str,
    text: str,
    *,
    param: str | None = None,
    meta: str | None = None,
    extra_html: str = "",
) -> str:
    main_parts = [
        f'<span class="speaker">{esc(speaker)}</span>',
        f'<span class="bubble-text">{esc(text)}</span>',
    ]
    if param:
        main_parts.append(f'<code class="bubble-param">{esc(param)}</code>')
    main = f'<div class="bubble-main">{"".join(main_parts)}</div>'
    meta_html = f'<div class="bubble-meta">{esc(meta)}</div>' if meta else ""
    return f"{main}{extra_html}{meta_html}"


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
) -> str:
    css = role if role in {ROLE_USER, ROLE_ASSISTANT, ROLE_SYSTEM} else ROLE_ASSISTANT
    speaker = label or css
    inner = _compact_bubble_body(speaker, body, meta=_format_run_time(start_time))
    return _chat_row(css, inner)


def _llm_bubble_items(
    run: dict[str, Any],
    ctx: AgentConversationContext,
    seen_users: set[str],
    *,
    include_user: bool = True,
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
                _bubble(ROLE_USER, last_user, label="User", start_time=run.get("start_time")),
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
    return _format_tool_target_display(path)


def _todos_list_html(run: dict[str, Any]) -> str:
    inputs = run.get("inputs")
    if not isinstance(inputs, dict):
        return ""
    todos = inputs.get("todos")
    if not isinstance(todos, list) or not todos:
        return ""
    items: list[str] = []
    for todo in todos:
        if not isinstance(todo, dict):
            continue
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
    return f'<ul class="todo-list compact">{"".join(items)}</ul>'


def _activity_chip(run: dict[str, Any], ctx: AgentConversationContext) -> str:
    meta = run.get("metadata") or {}
    if not isinstance(meta, dict):
        meta = {}
    icon_kind = tool_icon_kind(run)
    tool_name = str(meta.get("tool_name") or run.get("name") or "").strip()
    skill_id = str(meta.get("skill_id") or "").strip()
    kind = esc(run.get("run_type", "run"))
    status = esc(run.get("status", ""))
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
    summary = f"{kind}: {display_name} ({status}){extra}"
    target = _tool_target_detail(run)
    todos_html = ""
    if icon_kind == ICON_KIND_WRITE_TODOS:
        todos_html = _todos_list_html(run)
    inner = _compact_bubble_body(
        speaker,
        summary,
        param=target,
        meta=_format_run_time(run.get("start_time")),
        extra_html=todos_html,
    )
    bubble_class = f"{ROLE_TOOL} {icon_kind}"
    return _chat_row(
        ROLE_TOOL,
        inner,
        avatar_html=tool_avatar_html(icon_kind),
        bubble_class=bubble_class,
    )
