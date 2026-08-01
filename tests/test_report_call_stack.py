"""Unit tests for Trace report call-stack tree builder."""

from __future__ import annotations

from agentsmith_trace_server.report_call_stack import (
    ROLE_CLASS,
    ROLE_METHOD,
    ROLE_ROOT,
    ROLE_SKILL,
    ROLE_SKILL_REF,
    build_stack_forest,
    classify_role,
    is_skill_reference,
)


def _run(
    run_id: str,
    *,
    name: str = "",
    parent: str | None = None,
    activity: str | None = None,
    run_type: str = "tool",
    start: str = "2026-07-26T10:00:00+00:00",
    phase: str | None = None,
    path: str | None = None,
    skill_usage: str | None = None,
    skill_id: str | None = None,
    trace_id: str = "trace-1",
) -> dict:
    meta: dict = {"trace_id": trace_id}
    if activity:
        meta["activity_kind"] = activity
    if phase:
        meta["phase"] = phase
    if path:
        meta["path"] = path
    if skill_usage:
        meta["skill_usage"] = skill_usage
    if skill_id:
        meta["skill_id"] = skill_id
    return {
        "run_id": run_id,
        "parent_run_id": parent,
        "name": name or run_id,
        "run_type": run_type,
        "status": "success",
        "start_time": start,
        "metadata": meta,
        "inputs": {},
        "outputs": {},
    }


def test_classify_skill_reference_from_path() -> None:
    run = _run(
        "r1",
        activity="skill_used",
        skill_id="action-finder",
        path="/skills/action-finder/references/crud-templates.md",
    )
    assert is_skill_reference(run) is True
    assert classify_role(run) == ROLE_SKILL_REF


def test_build_stack_with_explicit_parents() -> None:
    runs = [
        _run("root", name="turn_prompt", activity="turn_prompt", start="2026-07-26T10:00:00+00:00"),
        _run(
            "sub",
            name="action-analyst",
            activity="subagent_task",
            parent="root",
            phase="started",
            start="2026-07-26T10:00:01+00:00",
        ),
        _run(
            "skill",
            name="action-finder",
            activity="skill_used",
            parent="sub",
            skill_id="action-finder",
            start="2026-07-26T10:00:02+00:00",
        ),
        _run(
            "ref",
            name="crud-templates.md",
            activity="skill_used",
            parent="sub",
            skill_id="action-finder",
            skill_usage="reference",
            path="/skills/action-finder/references/crud-templates.md",
            start="2026-07-26T10:00:03+00:00",
        ),
        _run(
            "llm",
            name="ChatOpenAI",
            run_type="llm",
            parent="sub",
            start="2026-07-26T10:00:04+00:00",
        ),
    ]
    forest = build_stack_forest(runs)
    assert len(forest) == 1
    root = forest[0]
    assert root.role == ROLE_ROOT
    assert len(root.children) == 1
    sub = root.children[0]
    assert sub.role == ROLE_CLASS
    roles = {c.role for c in sub.children}
    assert ROLE_SKILL in roles
    assert ROLE_SKILL_REF in roles
    assert ROLE_METHOD in roles


def test_heuristic_nests_orphan_under_subagent() -> None:
    runs = [
        _run("root", name="turn_prompt", activity="turn_prompt", start="2026-07-26T10:00:00+00:00"),
        _run(
            "sub",
            name="action-analyst",
            activity="subagent_task",
            parent="root",
            phase="started",
            start="2026-07-26T10:00:01+00:00",
        ),
        _run(
            "llm",
            name="ChatOpenAI",
            run_type="llm",
            parent=None,
            start="2026-07-26T10:00:02+00:00",
        ),
        _run(
            "sub-done",
            name="action-analyst",
            activity="subagent_task",
            parent="root",
            phase="completed",
            start="2026-07-26T10:00:05+00:00",
        ),
    ]
    forest = build_stack_forest(runs)
    assert forest[0].role == ROLE_ROOT
    # orphan llm should nest under an open subagent frame
    found = False
    for node in forest[0].children:
        if any(c.run["run_id"] == "llm" for c in node.children):
            found = True
    assert found is True
