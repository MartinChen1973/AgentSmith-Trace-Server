"""Call-stack tree build and role classification for Trace report runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

ACTIVITY_KIND_KEY = "activity_kind"
SKILL_USAGE_KEY = "skill_usage"
SKILL_USAGE_REFERENCE = "reference"
PATH_KEY = "path"
SKILL_ID_KEY = "skill_id"
REFERENCE_NAME_KEY = "reference_name"
TRACE_ID_KEY = "trace_id"
PARENT_KEY = "parent_run_id"
RUN_ID_KEY = "run_id"
START_KEY = "start_time"
META_KEY = "metadata"
RUN_TYPE_KEY = "run_type"
NAME_KEY = "name"
STATUS_KEY = "status"
PHASE_KEY = "phase"

KIND_TURN_PROMPT = "turn_prompt"
KIND_USER_MESSAGE = "user_message"
KIND_SUBAGENT = "subagent_task"
KIND_SKILL = "skill_used"
KIND_TURN_COMPLETE = "turn_complete"
KIND_TODOS = "deep_agent_todos"
PHASE_STARTED = "started"
PHASE_COMPLETED = "completed"
PHASE_FAILED = "failed"

ROLE_ROOT = "root"
ROLE_CLASS = "class"
ROLE_METHOD = "method"
ROLE_SKILL = "skill"
ROLE_SKILL_REF = "skill-ref"

REFERENCES_SEGMENT = "/references/"
SKILLS_SEGMENT = "/skills/"


@dataclass
class StackNode:
    run: dict[str, Any]
    role: str
    children: list[StackNode] = field(default_factory=list)


def metadata_of(run: dict[str, Any]) -> dict[str, Any]:
    meta = run.get(META_KEY) or {}
    return meta if isinstance(meta, dict) else {}


def activity_kind(run: dict[str, Any]) -> str:
    raw = metadata_of(run).get(ACTIVITY_KIND_KEY)
    return str(raw).strip() if raw is not None else ""


def skill_path(run: dict[str, Any]) -> str:
    meta = metadata_of(run)
    for key in (PATH_KEY, REFERENCE_NAME_KEY):
        val = meta.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    payload = (run.get("inputs") or {}).get("payload")
    if isinstance(payload, dict):
        val = payload.get(PATH_KEY)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def is_skill_reference(run: dict[str, Any]) -> bool:
    meta = metadata_of(run)
    usage = meta.get(SKILL_USAGE_KEY)
    if isinstance(usage, str) and usage.strip().lower() == SKILL_USAGE_REFERENCE:
        return True
    path = skill_path(run).replace("\\", "/")
    return REFERENCES_SEGMENT in path and SKILLS_SEGMENT in path


def reference_label(run: dict[str, Any]) -> str:
    meta = metadata_of(run)
    named = meta.get(REFERENCE_NAME_KEY)
    if isinstance(named, str) and named.strip():
        return named.strip()
    path = skill_path(run).replace("\\", "/")
    if not path:
        return "reference"
    return path.rsplit("/", 1)[-1] or "reference"


def classify_role(run: dict[str, Any]) -> str:
    kind = activity_kind(run)
    if kind == KIND_TURN_PROMPT:
        return ROLE_ROOT
    if kind == KIND_SUBAGENT:
        return ROLE_CLASS
    if kind == KIND_SKILL or metadata_of(run).get(SKILL_ID_KEY):
        if is_skill_reference(run):
            return ROLE_SKILL_REF
        if kind == KIND_SKILL:
            return ROLE_SKILL
    return ROLE_METHOD


def parse_time(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _sort_key(run: dict[str, Any]) -> tuple:
    t = parse_time(run.get(START_KEY))
    return (t or datetime.min, str(run.get(RUN_ID_KEY) or ""))


def build_children_map(
    runs: list[dict[str, Any]],
) -> tuple[dict[str, list[str]], list[str]]:
    by_id = {str(r.get(RUN_ID_KEY)): r for r in runs if r.get(RUN_ID_KEY)}
    children: dict[str, list[str]] = {rid: [] for rid in by_id}
    roots: list[str] = []
    for run in sorted(runs, key=_sort_key):
        rid = str(run.get(RUN_ID_KEY) or "")
        if not rid:
            continue
        parent = run.get(PARENT_KEY)
        parent_s = str(parent) if parent else ""
        if parent_s and parent_s in by_id and parent_s != rid:
            children[parent_s].append(rid)
        else:
            roots.append(rid)
    return children, roots


def _subagent_windows(
    runs: list[dict[str, Any]],
) -> list[tuple[str, datetime | None, datetime | None]]:
    windows: list[tuple[str, datetime | None, datetime | None]] = []
    open_frames: dict[str, tuple[str, datetime | None]] = {}
    for run in sorted(runs, key=_sort_key):
        if activity_kind(run) != KIND_SUBAGENT:
            continue
        rid = str(run.get(RUN_ID_KEY) or "")
        phase = str(metadata_of(run).get(PHASE_KEY) or "").strip()
        started_at = parse_time(run.get(START_KEY))
        name = str(run.get(NAME_KEY) or rid)
        if phase == PHASE_STARTED or phase == "":
            open_frames[name] = (rid, started_at)
            windows.append((rid, started_at, None))
        if phase in (PHASE_COMPLETED, PHASE_FAILED):
            prior = open_frames.pop(name, None)
            target = prior[0] if prior else rid
            for i, (wid, start, end) in enumerate(windows):
                if wid == target and end is None:
                    windows[i] = (wid, start, parse_time(run.get(START_KEY)))
                    break
            else:
                windows.append((target, started_at, parse_time(run.get(START_KEY))))
    return windows


def _active_subagent_at(
    when: datetime | None,
    windows: list[tuple[str, datetime | None, datetime | None]],
) -> str | None:
    if when is None:
        return None
    for rid, start, end in reversed(windows):
        if start and when < start:
            continue
        if end and when > end:
            continue
        if start and when >= start and (end is None or when <= end):
            return rid
    return None


def attach_orphan_runs(
    runs: list[dict[str, Any]],
    children: dict[str, list[str]],
    roots: list[str],
) -> list[str]:
    ## ⬇️ Nest unparented LLM/tool/skill under open SubAgent or turn_prompt by time
    by_id = {str(r.get(RUN_ID_KEY)): r for r in runs if r.get(RUN_ID_KEY)}
    windows = _subagent_windows(runs)
    prompt_roots = [
        str(r.get(RUN_ID_KEY))
        for r in runs
        if activity_kind(r) == KIND_TURN_PROMPT and r.get(RUN_ID_KEY)
    ]
    claimed = {cid for kids in children.values() for cid in kids}
    new_roots: list[str] = []
    for rid in roots:
        if rid in claimed:
            continue
        run = by_id.get(rid)
        if not run:
            continue
        if activity_kind(run) in (KIND_TURN_PROMPT,):
            new_roots.append(rid)
            continue
        when = parse_time(run.get(START_KEY))
        parent = _active_subagent_at(when, windows)
        if not parent and prompt_roots:
            parent = prompt_roots[0]
        if parent and parent in by_id and parent != rid and rid not in children.get(parent, []):
            children.setdefault(parent, []).append(rid)
            claimed.add(rid)
        else:
            new_roots.append(rid)
    ## ⬇️ Keep prompt roots first
    ordered: list[str] = []
    for pid in prompt_roots:
        if pid in new_roots and pid not in ordered:
            ordered.append(pid)
    for rid in new_roots:
        if rid not in ordered:
            ordered.append(rid)
    return ordered


def build_stack_forest(runs: list[dict[str, Any]]) -> list[StackNode]:
    dict_runs = [dict(r) for r in runs]
    children, roots = build_children_map(dict_runs)
    roots = attach_orphan_runs(dict_runs, children, roots)
    by_id = {str(r.get(RUN_ID_KEY)): r for r in dict_runs if r.get(RUN_ID_KEY)}
    seen: set[str] = set()

    def walk(rid: str) -> StackNode | None:
        if rid in seen or rid not in by_id:
            return None
        seen.add(rid)
        run = by_id[rid]
        node = StackNode(run=run, role=classify_role(run))
        kid_ids = sorted(children.get(rid, []), key=lambda i: _sort_key(by_id.get(i, {})))
        for kid in kid_ids:
            child = walk(kid)
            if child:
                node.children.append(child)
        return node

    forest: list[StackNode] = []
    for rid in roots:
        node = walk(rid)
        if node:
            forest.append(node)
    for rid, run in by_id.items():
        if rid not in seen:
            node = walk(rid)
            if node:
                forest.append(node)
    return forest
