"""Extract display summaries for tool runs in the conversation view."""

from __future__ import annotations

from typing import Any

FILE_PATH_KEYS = ("file_path", "path", "filepath", "filename")
GLOB_KEYS = ("glob", "glob_pattern", "pattern")
META_ARGS_PREVIEW = "args_preview"
META_PATH = "path"
META_SKILL_ID = "skill_id"
META_TOOL_NAME = "tool_name"
INPUT_PAYLOAD = "payload"
TOOL_READ_FILE = "read_file"
SKILL_MD_SUFFIX = "/SKILL.md"


def _non_empty_str(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _path_from_mapping(data: dict[str, Any]) -> str | None:
    for key in FILE_PATH_KEYS:
        found = _non_empty_str(data.get(key))
        if found:
            return found
    for key in GLOB_KEYS:
        found = _non_empty_str(data.get(key))
        if found:
            return f"glob: {found}"
    return None


def _path_from_args_preview(text: str) -> str | None:
    stripped = text.strip()
    if not stripped:
        return None
    for key in FILE_PATH_KEYS:
        for quote in ("'", '"'):
            marker = f"{quote}{key}{quote}: {quote}"
            idx = stripped.find(marker)
            if idx >= 0:
                start = idx + len(marker)
                end = stripped.find(quote, start)
                if end > start:
                    return stripped[start:end]
    return None


def _skill_read_path(meta: dict[str, Any], run_name: str) -> str | None:
    skill_id = _non_empty_str(meta.get(META_SKILL_ID))
    tool_name = _non_empty_str(meta.get(META_TOOL_NAME)) or _non_empty_str(run_name)
    if skill_id and tool_name == TOOL_READ_FILE:
        return f"/skills/{skill_id}{SKILL_MD_SUFFIX}"
    return None


def tool_run_detail(run: dict[str, Any]) -> str | None:
    inputs = run.get("inputs")
    meta = run.get("metadata")
    if not isinstance(inputs, dict):
        inputs = {}
    if not isinstance(meta, dict):
        meta = {}

    found = _path_from_mapping(inputs)
    if found:
        return found

    payload = inputs.get(INPUT_PAYLOAD)
    if isinstance(payload, dict):
        found = _path_from_mapping(payload)
        if found:
            return found
        preview = _non_empty_str(payload.get(META_ARGS_PREVIEW))
        if preview:
            found = _path_from_args_preview(preview)
            if found:
                return found

    found = _non_empty_str(meta.get(META_PATH))
    if found:
        return found

    preview = _non_empty_str(meta.get(META_ARGS_PREVIEW))
    if preview:
        found = _path_from_args_preview(preview)
        if found:
            return found

    return _skill_read_path(meta, str(run.get("name") or ""))
