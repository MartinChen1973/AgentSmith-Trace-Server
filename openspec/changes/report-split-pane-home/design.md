## Context

当前 `/report` 为单列表页，线程详情在独立路由。管理员希望在首页同时看到全局活动与某一 thread 的会话。

## Goals / Non-Goals

**Goals:**

- `/report` 左右分栏：左=整体日志，右=选中 thread 会话。
- 点击左侧线程更新右侧，无需多级跳转。
- 会话可读（角色/内容）；可展开 run 细节。

**Non-Goals:**

- SPA / WebSocket 实时刷新。
- 改动 ingestion API 或事件 schema。

## Decisions

1. **服务端渲染 + query 参数** — `/report?thread_id=…&user_id=…&run_id=…`，与现有风格一致。
2. **左侧** — 按用户分组的线程列表（最近活动降序），行链接带 `thread_id`。
3. **右侧** — 优先对话气泡（来自 LLM run 的 messages/outputs），下方保留可展开 run 树。
4. **文件拆分** — 将样式与分栏页面从过长的 `report_view.py` 中拆出，遵守文件长度约束。
5. **旧路由** — `/report/users/{id}`、`/report/threads/{id}` 重定向到分栏首页对应 query，避免书签失效。

## Risks / Trade-offs

- [全页刷新略闪] → 可接受；后续可 HTMX。
- [对话合成不完整若无 LLM run] → 仍展示 run 树与 activity 元数据。

## Migration Plan

部署后刷新 `/report` 即可；旧 URL 重定向到新首页。

## Open Questions

- 无。
