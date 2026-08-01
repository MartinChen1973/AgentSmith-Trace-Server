"""Emoji and SVG icons for tool and activity rows in the report conversation view."""

from __future__ import annotations

import html
from typing import Any

ACTIVITY_SKILL_USED = "skill_used"
ACTIVITY_TOOL_USED = "tool_used"
ACTIVITY_TODOS = "deep_agent_todos"
ACTIVITY_SUBAGENT = "subagent_task"
ACTIVITY_SUBAGENT_ALT = "subagent"

ICON_KIND_SKILL = "skill"
ICON_KIND_READ_FILE = "read_file"
ICON_KIND_WRITE_FILE = "write_file"
ICON_KIND_EDIT_FILE = "edit_file"
ICON_KIND_WRITE_TODOS = "write_todos"
ICON_KIND_TASK = "task"
ICON_KIND_GLOB = "glob"
ICON_KIND_GREP = "grep"
ICON_KIND_EXECUTE = "execute"
ICON_KIND_LS = "ls"
ICON_KIND_TOOL = "tool"

TOOL_NAME_TO_ICON_KIND = {
    "read_file": ICON_KIND_READ_FILE,
    "write_file": ICON_KIND_WRITE_FILE,
    "edit_file": ICON_KIND_EDIT_FILE,
    "write_todos": ICON_KIND_WRITE_TODOS,
    "task": ICON_KIND_TASK,
    "glob": ICON_KIND_GLOB,
    "grep": ICON_KIND_GREP,
    "execute": ICON_KIND_EXECUTE,
    "ls": ICON_KIND_LS,
}

ICON_KIND_LABEL = {
    ICON_KIND_SKILL: "Skill",
    ICON_KIND_READ_FILE: "Read file",
    ICON_KIND_WRITE_FILE: "Write file",
    ICON_KIND_EDIT_FILE: "Edit file",
    ICON_KIND_WRITE_TODOS: "Todo list",
    ICON_KIND_TASK: "Sub-agent task",
    ICON_KIND_GLOB: "Glob",
    ICON_KIND_GREP: "Grep",
    ICON_KIND_EXECUTE: "Execute",
    ICON_KIND_LS: "List files",
    ICON_KIND_TOOL: "Tool",
}

# ## ⬇️ Match ai-end tool attribution (`TOOL_ATTRIBUTION_ICON` in config.py)
ICON_KIND_EMOJI = {
    ICON_KIND_SKILL: "🛠️",
}

SVG_CLIP_LIST = (
    '<svg class="tool-inline-svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2m-6 7h6m-6 4h6"/>'
    "</svg>"
)
SVG_BOOK_OPEN = (
    '<svg class="tool-inline-svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M12 6.5a2 2 0 0 1 2-2h5v14h-5a2 2 0 0 0-2 2v0a2 2 0 0 0 2 2h5V6.5Zm-2 0H5v14h5a2 2 0 0 1 2 2v0a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-12a2 2 0 0 1 2-2h5Z"/>'
    "</svg>"
)
SVG_PENCIL_WRITE = (
    '<svg class="tool-inline-svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M16 3l5 5-12 12H4v-4L16 3Zm0 2.8L6 16v2h2l10-10-2-2Z"/>'
    "</svg>"
)
SVG_PENCIL_EDIT = (
    '<svg class="tool-inline-svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M3 17.25V21h3.75L17.8 9.94l-3.75-3.75L3 17.25ZM20.7 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83Z"/>'
    "</svg>"
)
SVG_TARGET = (
    '<svg class="tool-inline-svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm0 4a6 6 0 1 1 0 12 6 6 0 0 1 0-12Zm0 3a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/>'
    "</svg>"
)
SVG_SEARCH = (
    '<svg class="tool-inline-svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M10 4a6 6 0 1 0 3.87 10.6l4.39 4.39 1.41-1.41-4.39-4.39A6 6 0 0 0 10 4Zm0 2a4 4 0 1 1 0 8 4 4 0 0 1 0-8Z"/>'
    "</svg>"
)
SVG_FOLDER = (
    '<svg class="tool-inline-svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M10 4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h6Z"/>'
    "</svg>"
)
SVG_BOLT = (
    '<svg class="tool-inline-svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M13 2 3 14h7l-1 8 10-12h-7l1-8Z"/>'
    "</svg>"
)
SVG_WRENCH = (
    '<svg class="tool-inline-svg" viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M22.7 19.3l-5.4-5.4c1.7-2.5 1.2-5.9-.8-7.9-2-2-5.4-2.5-7.9-.8l-5.4-5.4c-.4-.4-1-.4-1.4 0l-1.4 1.4c-.4.4-.4 1 0 1.4l5.4 5.4c-1.7 2.5-1.2 5.9.8 7.9 2 2 5.4 2.5 7.9.8l5.4 5.4c.4.4 1 .4 1.4 0l1.4-1.4c.4-.4.4-1 0-1.4Z"/>'
    "</svg>"
)

ICON_KIND_SVG = {
    ICON_KIND_READ_FILE: SVG_BOOK_OPEN,
    ICON_KIND_WRITE_FILE: SVG_PENCIL_WRITE,
    ICON_KIND_EDIT_FILE: SVG_PENCIL_EDIT,
    ICON_KIND_WRITE_TODOS: SVG_CLIP_LIST,
    ICON_KIND_TASK: SVG_TARGET,
    ICON_KIND_GLOB: SVG_SEARCH,
    ICON_KIND_GREP: SVG_SEARCH,
    ICON_KIND_EXECUTE: SVG_BOLT,
    ICON_KIND_LS: SVG_FOLDER,
    ICON_KIND_TOOL: SVG_WRENCH,
}


def tool_icon_kind(run: dict[str, Any]) -> str:
    meta = run.get("metadata")
    meta_dict = meta if isinstance(meta, dict) else {}
    activity = str(meta_dict.get("activity_kind") or "").strip().lower()
    tool_name = str(meta_dict.get("tool_name") or run.get("name") or "").strip().lower()

    if activity == ACTIVITY_SKILL_USED:
        return ICON_KIND_SKILL
    if activity == ACTIVITY_TODOS:
        return ICON_KIND_WRITE_TODOS
    if activity in (ACTIVITY_SUBAGENT, ACTIVITY_SUBAGENT_ALT):
        return ICON_KIND_TASK

    mapped = TOOL_NAME_TO_ICON_KIND.get(tool_name)
    if mapped:
        return mapped
    return ICON_KIND_TOOL


def _icon_inner_html(icon_kind: str) -> str:
    kind = icon_kind if icon_kind in ICON_KIND_SVG or icon_kind in ICON_KIND_EMOJI else ICON_KIND_TOOL
    emoji = ICON_KIND_EMOJI.get(kind)
    if emoji:
        return f'<span class="avatar-emoji" aria-hidden="true">{emoji}</span>'
    svg = ICON_KIND_SVG[kind]
    return f'<span class="avatar-icon-wrap" aria-hidden="true">{svg}</span>'


def tool_inline_icon_html(icon_kind: str) -> str:
    kind = icon_kind if icon_kind in ICON_KIND_SVG or icon_kind in ICON_KIND_EMOJI else ICON_KIND_TOOL
    label = ICON_KIND_LABEL.get(kind, "Tool")
    safe_label = html.escape(label)
    safe_kind = html.escape(kind)
    emoji = ICON_KIND_EMOJI.get(kind)
    inner = (
        f'<span class="avatar-emoji" aria-hidden="true">{emoji}</span>'
        if emoji
        else ICON_KIND_SVG[kind]
    )
    return (
        f'<span class="tool-inline-icon tool-inline-{safe_kind}" aria-label="{safe_label}">'
        f"{inner}</span>"
    )


def tool_avatar_html(icon_kind: str) -> str:
    kind = icon_kind if icon_kind in ICON_KIND_SVG or icon_kind in ICON_KIND_EMOJI else ICON_KIND_TOOL
    label = ICON_KIND_LABEL.get(kind, "Tool")
    safe_kind = html.escape(kind)
    safe_label = html.escape(label)
    return (
        f'<div class="chat-avatar chat-avatar-tool chat-avatar-{safe_kind}" '
        f'aria-label="{safe_label}">'
        f"{_icon_inner_html(kind)}"
        "</div>"
    )


def tool_bubble_label(icon_kind: str) -> str:
    return ICON_KIND_LABEL.get(icon_kind, ICON_KIND_LABEL[ICON_KIND_TOOL])
