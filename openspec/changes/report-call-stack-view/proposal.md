## Why

Trace「运行详情」目前以扁平时间线展示运行记录，即便存在 `parent_run_id` 也仅靠左边距缩进，难以按 DeepAgent → SubAgent → LLM/工具/技能 的调用栈阅读。需要将线程运行渲染为类调用栈的层级结构，并突出 SubAgent 与技能（含 references）节点。

## What Changes

- 将线程「运行详情」从扁平列表改为嵌套调用栈视图：DeepAgent 回合为根，SubAgent 为显著的「类」节点，LLM 与普通工具为方法级子节点。
- 对 `skill_used` 使用专用技能标记；当路径指向 `/skills/<id>/references/` 时，渲染为技能下的 reference 用法节点。
- 在缺少完整 `parent_run_id` 时，按同一 `trace_id` 与时间窗口做尽力而为的归属（挂到进行中的 SubAgent 或 DeepAgent 根），避免栈完全塌成平铺。
- 会话聊天气泡区保持现有行为（不强制改成调用栈）。

## Capabilities

### New Capabilities

- （无）

### Modified Capabilities

- `trace-report-ui`: 线程运行详情以调用栈层级展示 DeepAgent / SubAgent / LLM·工具 / 技能与技能 reference。

## Impact

- `report_panels.py`、`report_styles.py`；必要时微调 `report_view.py` 文案。
- 依赖 SEAI/ai-end 侧更完整的 `parent_run_id` 与技能 reference 元数据以获得最佳效果；报告端保留启发式回退。
- 无 ingestion API 破坏性变更。
