"""Resolve DeepAgent / sub-agent display labels for report conversation rows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentsmith_trace_server.report_call_stack import (
    KIND_SUBAGENT,
    PHASE_COMPLETED,
    PHASE_FAILED,
    PHASE_STARTED,
    activity_kind,
    metadata_of,
)

META_DEEPAGENT = "deepagent"
META_AGENT_SCOPE = "agent_scope"
META_AGENT_NAME = "agent_name"
META_SUBAGENT_TYPE = "subagent_type"
META_LC_AGENT_NAME = "lc_agent_name"
META_LANGGRAPH_NODE = "langgraph_node"
META_PHASE = "phase"

GENERIC_LLM_NAMES = frozenset(
    {
        "llm",
        "chatopenai",
        "unknown-model",
    }
)


@dataclass
class AgentConversationContext:
    deepagent: str | None = None
    active_subagent: str | None = None


def _meta_str(meta: dict[str, Any], key: str) -> str:
    val = meta.get(key)
    return str(val).strip() if val is not None else ""


def update_agent_context(ctx: AgentConversationContext, run: dict[str, Any]) -> None:
    meta = metadata_of(run)
    deep = _meta_str(meta, META_DEEPAGENT)
    if deep:
        ctx.deepagent = deep
    activity = activity_kind(run)
    if activity == KIND_SUBAGENT:
        sub = _meta_str(meta, META_SUBAGENT_TYPE) or _meta_str(meta, META_AGENT_NAME)
        phase = _meta_str(meta, META_PHASE).lower()
        if phase in ("", PHASE_STARTED):
            if sub:
                ctx.active_subagent = sub
        elif phase in (PHASE_COMPLETED, PHASE_FAILED):
            if sub and ctx.active_subagent == sub:
                ctx.active_subagent = None
    scope = _meta_str(meta, META_AGENT_SCOPE).lower()
    if scope == "subagent":
        sub = _meta_str(meta, META_SUBAGENT_TYPE) or _meta_str(meta, META_AGENT_NAME)
        if sub:
            ctx.active_subagent = sub


def _identity_from_meta(meta: dict[str, Any]) -> tuple[str | None, str | None]:
    sub = _meta_str(meta, META_SUBAGENT_TYPE)
    if sub:
        return "subagent", sub
    scope = _meta_str(meta, META_AGENT_SCOPE).lower()
    name = _meta_str(meta, META_AGENT_NAME)
    if scope == "subagent" and name:
        return "subagent", name
    if scope == "deep_agent" and name:
        return "deep_agent", name
    deep = _meta_str(meta, META_DEEPAGENT)
    if deep:
        return "deep_agent", deep
    lc = _meta_str(meta, META_LC_AGENT_NAME)
    if lc:
        return "agent", lc
    node = _meta_str(meta, META_LANGGRAPH_NODE)
    if node:
        return "agent", node
    return None, None


def _format_scope_label(scope: str | None, agent_id: str) -> str:
    if scope == "subagent":
        return f"Sub-agent · {agent_id}"
    if scope == "deep_agent":
        return f"DeepAgent · {agent_id}"
    return agent_id


def _is_generic_model_name(name: str) -> bool:
    normalized = name.strip().lower().replace("-", "").replace("_", "")
    if not normalized:
        return True
    if normalized in GENERIC_LLM_NAMES:
        return True
    if normalized.startswith("chat") and "openai" in normalized:
        return True
    return False


def deepagent_invoke_speaker_label(
    run: dict[str, Any],
    ctx: AgentConversationContext,
) -> str:
    meta = metadata_of(run)
    scope, agent_id = _identity_from_meta(meta)
    if agent_id and scope == "deep_agent":
        return f"DeepAgent · {agent_id}"
    if ctx.deepagent:
        return f"DeepAgent · {ctx.deepagent}"
    return "DeepAgent"


def assistant_speaker_label(
    run: dict[str, Any],
    ctx: AgentConversationContext,
) -> str:
    meta = metadata_of(run)
    scope, agent_id = _identity_from_meta(meta)
    if agent_id:
        return _format_scope_label(scope, agent_id)
    if ctx.active_subagent:
        return f"Sub-agent · {ctx.active_subagent}"
    if ctx.deepagent:
        return f"DeepAgent · {ctx.deepagent}"
    name = str(run.get("name") or "").strip()
    if name and not _is_generic_model_name(name):
        return name
    return "Assistant"


def tool_activity_speaker_label(
    run: dict[str, Any],
    ctx: AgentConversationContext,
    tool_label: str,
) -> str:
    meta = metadata_of(run)
    scope, agent_id = _identity_from_meta(meta)
    if not agent_id and ctx.active_subagent:
        scope, agent_id = "subagent", ctx.active_subagent
    elif not agent_id and ctx.deepagent:
        scope, agent_id = "deep_agent", ctx.deepagent
    if not agent_id:
        return tool_label
    if scope == "deep_agent":
        return f"DeepAgent · {agent_id} · {tool_label}"
    return f"{agent_id} · {tool_label}"
