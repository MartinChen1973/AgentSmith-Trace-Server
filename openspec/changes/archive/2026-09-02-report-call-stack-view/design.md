## Context

报告「运行详情」按 `start_time` 平铺 `<details>`，仅用 `parent_run_id` 计算左边距。SEAI 活动多数无父链接；LLM/工具回调可能有 LangChain 父链。产品期望 IDE 式调用栈：DeepAgent 根、SubAgent 如类、LLM/工具如方法、技能与 references 可辨。

## Goals / Non-Goals

**Goals:**

- 嵌套 DOM 调用栈，节点角色可区分（root / class / method / skill / skill-ref）。
- 优先使用 `parent_run_id`；缺失时对同 `trace_id` 做时间窗启发式挂载。
- 从 metadata/`path` 识别技能 reference（`/skills/.../references/`）。

**Non-Goals:**

- 改造会话气泡为调用栈。
- 修改 ingestion schema。
- 在本变更中实现 SEAI 父链写入（由姊妹变更负责）。

## Decisions

### 1. 树构建：显式父链优先，启发式补全

**Decision:** 先按 `parent_run_id` 建树；将无父且同 `trace_id` 的孤儿挂到：进行中的 `subagent_task`（start≤t＜complete），否则挂到 `turn_prompt`/`deep_agent` 根，再否则作为并列根。

**Alternatives:** 仅缩进 — 拒绝。仅启发式忽略 parent — 拒绝。

### 2. 节点角色分类

| 角色 | 判定 |
|------|------|
| root | `activity_kind=turn_prompt` 或无父的 deep_agent 回合根 |
| class | `activity_kind=subagent_task` |
| skill | `activity_kind=skill_used` 且非 reference |
| skill-ref | `skill_usage=reference` 或 path 含 `/references/` |
| method | `run_type` 为 llm/tool 的其余节点 |
| chain | `turn_complete` 等挂在根下作方法/尾声 |

### 3. 视觉

**Decision:** 嵌套 `<ul class="call-stack">` + `<details>`；class 节点更粗边框/更大字重；skill 与 skill-ref 使用不同 pill 文案（`skill` / `ref`）。

## Risks / Trade-offs

- [启发式误挂] → 显式 parent 优先；启发式仅填补孤儿。
- [重复 SDK 工具与 SEAI 活动] → 同名并列保留；后续可去重。

## Migration Plan

部署 Trace Server 即可；旧数据在无 parent 时仍可启发式成栈。回滚恢复扁平 `render_runs_list`。

## Open Questions

- 是否在会话区同步缩略栈 — 默认否。
