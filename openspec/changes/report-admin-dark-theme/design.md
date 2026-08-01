## Context

`/report` 已实现左右分栏；视觉仍为浅色。目标是复用 SEAI `packages/ai-end/api/static/admin.html` 的 CSS 变量与排版习惯。

## Goals / Non-Goals

**Goals:**

- 报告页 `:root` 变量与 ai-end Admin 对齐（`--bg` `#0f1419`、`--surface` `#1a2332`、`--border` `#2d3a4d`、`--text` `#e7ecf3`、`--muted` `#8b9cae`、`--accent` `#5b9fd4`、Segoe UI）。
- 顶栏、线程卡片、聊天气泡、run 面板、代码块在深色背景下可读。

**Non-Goals:**

- 复制 Admin 的 catalog 列布局或交互。
- 引入外部 CSS 框架。

## Decisions

1. **仅改样式模块** — 集中更新 `report_styles.py`，页面结构保持分栏。
2. **语义色** — success/error 气泡与 pill 使用 Admin 的 `--ok` / `--err`；用户/助手气泡用 surface 变体。
3. **顶栏标题** — 文案改为 `AgentSmith-Trace · Admin`，字号接近 Admin `h1`（约 1.15rem / weight 600）。

## Risks / Trade-offs

- [深色下对比不足] → 沿用 Admin 已验证 token，代码块保持深底浅字。

## Migration Plan

重启 Trace Server 后硬刷新 `/report`。

## Open Questions

- 无。
