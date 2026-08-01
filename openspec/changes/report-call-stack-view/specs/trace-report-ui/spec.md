## ADDED Requirements

### Requirement: Thread runs render as a call stack

The thread run details section of the report SHALL render runs as a nested call-stack tree rather than a solely flat chronological list with margin indentation.

#### Scenario: Nested ownership is visible

- **WHEN** a thread's runs include parent-child links via `parent_run_id`
- **THEN** the report SHALL nest child runs under their parent in the DOM
- **AND** SHALL preserve expandable detail panels for each node

### Requirement: Distinguish DeepAgent, SubAgent, methods, and skills

The call-stack view SHALL visually distinguish DeepAgent root nodes, SubAgent class-like nodes, LLM/tool method-like nodes, and skill nodes.

#### Scenario: SubAgent appears as a class-like frame

- **WHEN** a run has `metadata.activity_kind` equal to `subagent_task`
- **THEN** the call-stack view SHALL render it with a class-like emphasis distinct from ordinary tool/LLM method rows

#### Scenario: Skill nodes are marked

- **WHEN** a run has `metadata.activity_kind` equal to `skill_used`
- **THEN** the call-stack view SHALL show a skill marker (pill or equivalent) including the skill id when present

### Requirement: Mark skill reference usages

When a skill-related run indicates a references path (metadata `skill_usage` of `reference`, or a path under `/skills/<id>/references/`), the call-stack view SHALL mark it as a skill reference usage.

#### Scenario: Reference path is labeled

- **WHEN** a skill run's path or metadata identifies a file under a skill `references` directory
- **THEN** the call-stack view SHALL label the node as a reference usage (for example a `ref` pill)
- **AND** SHOULD show a concise reference name derived from the path when available

### Requirement: Heuristic nesting when parents are missing

When runs share a `trace_id` but lack `parent_run_id`, the call-stack view SHALL attempt to nest orphan LLM/tool/skill runs under an in-progress SubAgent or the DeepAgent turn root using timestamps, without inventing false cross-trace links.

#### Scenario: Orphan tools nest under open SubAgent

- **WHEN** an unparented tool or LLM run occurs after a SubAgent `started` event and before that SubAgent's `completed`/`failed` event in the same trace
- **THEN** the call-stack view SHALL nest that run under the SubAgent node when no explicit `parent_run_id` conflicts
