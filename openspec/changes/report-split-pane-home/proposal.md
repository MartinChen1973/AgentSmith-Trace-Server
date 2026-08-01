## Why

管理员总览目前是多级跳转（用户 → 线程 → 运行），无法在同一屏对照「整体活动」与「某一会话内容」，排查 SEAI / Deep Agent 会话效率低。

## What Changes

- 将 `/report` 改为左右分栏首页：左侧为整体性日志（用户/线程活动列表），右侧为选中 thread 的会话视图。
- 通过查询参数 `thread_id`（及可选 `user_id` / `run_id`）选择右侧会话；点击左侧线程即刷新右侧。
- 保留既有 `/report/users/...`、`/report/threads/...`、`/report/runs/...` 深度链接（可重定向或继续可用）。
- 右侧会话以可读对话为主，并可展开底层 run 详情。

## Capabilities

### New Capabilities

- （无）

### Modified Capabilities

- `trace-report-ui`: 总览页改为左右分栏；选中线程后右侧展示会话内容。

## Impact

- `report_view.py` / 可能拆分的视图模块、`api.py` 的 `/report` 处理、`db.py` 可能新增近期线程查询。
- 既有 API JSON 契约不变；HTML 导航体验变更。
