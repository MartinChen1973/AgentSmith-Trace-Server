"""Server-rendered HTML pages for the Trace admin report."""

from __future__ import annotations

from urllib.parse import quote

from agentsmith_trace_server.models import RunEvent, ThreadSummary, UserSummary
from agentsmith_trace_server.report_panels import (
    esc,
    render_conversation,
    render_run_panel,
    render_runs_list,
    report_home_href,
    run_to_dict,
)
from agentsmith_trace_server.report_styles import COMMON_STYLES, REPORT_CHAT_SCRIPT

PAGE_CLASS_SINGLE = "single"
PAGE_CLASS_SPLIT = "split-page"
EMPTY_SELECT_HINT = "请在左侧选择一个线程，以查看会话内容。"
TITLE_HOME = "AgentSmith-Trace · Admin"
HEADING_HOME = "AgentSmith-Trace · Admin"
SUB_HOME = "左侧为整体活动日志；右侧默认展示最近线程的调用栈与会话。"


def _page(title: str, body: str, *, crumbs: str = "", body_class: str = PAGE_CLASS_SINGLE) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <title>{esc(title)}</title>
  <style>{COMMON_STYLES}</style>
</head>
<body class="{esc(body_class)}">
  {crumbs}
  {body}
  <script>{REPORT_CHAT_SCRIPT}</script>
</body>
</html>"""


def report_home_html(
    users: list[UserSummary],
    threads_by_user: dict[str, list[ThreadSummary]],
    *,
    selected_thread_id: str | None = None,
    selected_user_id: str | None = None,
    selected_runs: list[RunEvent] | None = None,
    open_run_id: str | None = None,
) -> str:
    left = _left_overview_pane(
        users,
        threads_by_user,
        selected_thread_id=selected_thread_id,
    )
    right = _right_conversation_pane(
        selected_thread_id=selected_thread_id,
        selected_user_id=selected_user_id,
        runs=selected_runs or [],
        open_run_id=open_run_id,
    )
    body = f"""
    <div class="topbar">
      <div>
        <h1>{HEADING_HOME}</h1>
        <p class="sub">{SUB_HOME}</p>
      </div>
      <nav>
        <a href="/simulator">Simulator</a>
        <a href="/docs">Swagger UI</a>
        <a href="/health">Health</a>
      </nav>
    </div>
    <div class="split">
      <aside class="pane pane-left">{left}</aside>
      <section class="pane pane-right">{right}</section>
    </div>
    """
    return _page(TITLE_HOME, body, body_class=PAGE_CLASS_SPLIT)


def user_threads_html(user_id: str, threads: list[ThreadSummary]) -> str:
    ## ⬇️ Legacy full-page view (kept for tests / fallbacks)
    uid = quote(user_id, safe="")
    rows = ""
    for thread in threads:
        href = report_home_href(user_id=user_id, thread_id=thread.thread_id)
        rows += (
            f"<tr>"
            f'<td><a href="{esc(href)}">{esc(thread.thread_id)}</a></td>'
            f"<td>{thread.run_count}</td>"
            f"<td>{esc(thread.last_activity or '—')}</td>"
            f"</tr>"
        )
    if not rows:
        rows = '<tr><td colspan="3">该用户暂无线程记录。</td></tr>'
    crumbs = f'<div class="crumbs"><a href="/report">总览</a> / {esc(user_id)}</div>'
    body = f"""
    <h1>用户线程</h1>
    <p class="sub">User ID: <code>{esc(user_id)}</code></p>
    <table>
      <thead><tr><th>线程 ID</th><th>记录数</th><th>最近活动</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p><a href="/report/users/{uid}">刷新</a> · <a href="/report">返回总览</a></p>
    """
    return _page(f"用户 {user_id}", body, crumbs=crumbs)


def thread_detail_html(
    thread_id: str,
    runs: list[RunEvent],
    *,
    user_id: str | None = None,
    open_run_id: str | None = None,
) -> str:
    ## ⬇️ Legacy full-page thread view
    tid = quote(thread_id, safe="")
    crumbs_parts = ['<a href="/report">总览</a>']
    if user_id:
        crumbs_parts.append(
            f'<a href="{esc(report_home_href(user_id=user_id))}">{esc(user_id)}</a>'
        )
    crumbs_parts.append(esc(thread_id))
    crumbs = f'<div class="crumbs">{" / ".join(crumbs_parts)}</div>'
    user_line = f'<div>User: <code>{esc(user_id)}</code></div>' if user_id else ""
    body = f"""
    <h1>线程详情</h1>
    <p class="sub">Thread ID: <code>{esc(thread_id)}</code></p>
    <div class="session">
      {user_line}
      <div>Runs: <strong>{len(runs)}</strong></div>
      <div>API: <a href="/api/v1/threads/{tid}/runs">JSON</a></div>
    </div>
    <h2>会话</h2>
    {render_conversation(runs)}
    <h2>运行记录</h2>
    {render_runs_list(runs, open_run_id=open_run_id)}
    <p style="margin-top:1.5rem"><a href="{esc(report_home_href(thread_id=thread_id, user_id=user_id))}">分栏总览</a> · <a href="/report">返回总览</a></p>
    """
    return _page(f"线程 {thread_id}", body, crumbs=crumbs)


def run_detail_html(run: RunEvent, *, back_url: str | None = None) -> str:
    run_dict = run_to_dict(run)
    run_id = str(run_dict.get("run_id"))
    thread_id = run.metadata.get("thread_id")
    user_id = run.metadata.get("user_id")
    crumbs_parts = ['<a href="/report">总览</a>']
    if user_id:
        crumbs_parts.append(
            f'<a href="{esc(report_home_href(user_id=str(user_id)))}">{esc(user_id)}</a>'
        )
    if thread_id:
        crumbs_parts.append(
            f'<a href="{esc(report_home_href(user_id=str(user_id) if user_id else None, thread_id=str(thread_id)))}">{esc(thread_id)}</a>'
        )
    crumbs_parts.append(f"<code>{esc(run_id)}</code>")
    crumbs = f'<div class="crumbs">{" / ".join(crumbs_parts)}</div>'
    back = back_url or report_home_href(
        user_id=str(user_id) if user_id else None,
        thread_id=str(thread_id) if thread_id else None,
        run_id=run_id,
    )
    body = f"""
    <h1>运行详情</h1>
    <p class="sub">
      <span class="pill">{esc(run.run_type.value)}</span>
      <strong>{esc(run.name)}</strong>
      <span class="muted">{esc(run.status.value)}</span>
      <span class="muted">{esc(run.start_time.isoformat())}</span>
    </p>
    {render_run_panel(run_dict, show_detail_link=False)}
    <p style="margin-top:1.5rem">
      <a href="{esc(back)}">返回会话</a> ·
      <a href="/api/v1/runs/{esc(run_id)}">JSON API</a>
    </p>
    """
    return _page(f"Run {run_id[:8]}", body, crumbs=crumbs)


def _left_overview_pane(
    users: list[UserSummary],
    threads_by_user: dict[str, list[ThreadSummary]],
    *,
    selected_thread_id: str | None,
) -> str:
    if not users:
        return '<div class="empty">暂无数据。请运行 simulator 或 SEAI ai-end 发送 trace。</div>'
    blocks: list[str] = ["<h2>整体日志</h2>"]
    for user in users:
        blocks.append(_user_thread_block(user, threads_by_user.get(user.user_id, []), selected_thread_id))
    return "".join(blocks)


def _user_thread_block(
    user: UserSummary,
    threads: list[ThreadSummary],
    selected_thread_id: str | None,
) -> str:
    items: list[str] = []
    for thread in threads:
        href = report_home_href(user_id=user.user_id, thread_id=thread.thread_id)
        active = " active" if selected_thread_id == thread.thread_id else ""
        items.append(
            f'<li><a class="thread-link{active}" href="{esc(href)}">'
            f'<div class="thread-id">{esc(thread.thread_id)}</div>'
            f'<div class="thread-meta">{thread.run_count} 条 · {esc(thread.last_activity or "—")}</div>'
            f"</a></li>"
        )
    if not items:
        items.append("<li class='muted'>暂无线程</li>")
    return f"""
    <div class="user-block">
      <h2>{esc(user.user_id)} · {user.thread_count} 线程 · {user.run_count} 记录</h2>
      <ul class="thread-list">{"".join(items)}</ul>
    </div>
    """


def _right_conversation_pane(
    *,
    selected_thread_id: str | None,
    selected_user_id: str | None,
    runs: list[RunEvent],
    open_run_id: str | None,
) -> str:
    if not selected_thread_id:
        return f'<div class="empty">{EMPTY_SELECT_HINT}</div>'
    tid = quote(selected_thread_id, safe="")
    user_line = (
        f'<div>User: <code>{esc(selected_user_id)}</code></div>'
        if selected_user_id
        else ""
    )
    return f"""
    <div class="session">
      <div>Thread: <code>{esc(selected_thread_id)}</code></div>
      {user_line}
      <div>Runs: <strong>{len(runs)}</strong></div>
      <div>API: <a href="/api/v1/threads/{tid}/runs">JSON</a></div>
    </div>
    <h2 id="call-stack">调用栈</h2>
    <p class="sub">🤖 DeepAgent 根 → 🐜 SubAgent → LLM/工具/🛠️ 技能；展开节点查看详情。</p>
    {render_runs_list(runs, open_run_id=open_run_id)}
    <h2 id="conversation">会话</h2>
    {render_conversation(runs)}
    """
