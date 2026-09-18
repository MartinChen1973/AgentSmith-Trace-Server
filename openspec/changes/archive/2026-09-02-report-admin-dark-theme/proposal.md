## Why

AgentSmith-Trace 管理员报告页仍为浅色默认样式，与 SEAI `ai-end` `/admin` 的深色配色与文字风格不一致，本地多后台切换时观感割裂。

## What Changes

- 将报告页（分栏总览及单页详情）视觉主题对齐 `ai-end` Admin：深色背景、surface 面板、accent 链接、Segoe UI 字体栈与相近字号层级。
- 不改变分栏布局与功能路由。

## Capabilities

### New Capabilities

- （无）

### Modified Capabilities

- `trace-report-ui`: 管理员 HTML 报告页采用与 ai-end Admin 一致的深色配色与文字风格。

## Impact

- `report_styles.py` 为主；必要时微调 `report_view.py` 顶栏文案/结构。
- 无 API 变更。
