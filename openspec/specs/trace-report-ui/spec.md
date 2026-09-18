# trace-report-ui Specification

## Purpose
TBD - created by archiving change trace-report-dashboard. Update Purpose after archive.
## Requirements
### Requirement: Split-pane admin home

The server SHALL serve `/report` as a two-pane HTML layout: a left pane for overall activity logs and a right pane for the selected thread conversation.

#### Scenario: Open split home

- **WHEN** a browser navigates to `/` or `/report`
- **THEN** the server SHALL render a page with a left overview pane listing users and their threads by recent activity
- **AND** a right pane that shows an empty-state prompt when no thread is selected

#### Scenario: Select thread conversation

- **WHEN** a browser navigates to `/report?thread_id={thread_id}` (optionally with `user_id`)
- **THEN** the left pane SHALL highlight or mark the selected thread
- **AND** the right pane SHALL render that thread’s conversation content derived from recorded runs

#### Scenario: Conversation readability

- **WHEN** the right pane shows a selected thread that contains LLM runs with `inputs.messages` and `outputs`
- **THEN** the page SHALL present human-readable role-labeled message content suitable for debugging
- **AND** SHALL allow expanding underlying run records for full inputs/outputs/metadata

### Requirement: User overview report page

The server SHALL serve an HTML overview page as the left pane of `/report`, listing users and their threads with activity counts.

#### Scenario: Open report home

- **WHEN** a browser navigates to `/` or `/report`
- **THEN** the server SHALL render overall activity in the left pane, including each `user_id` with thread entries and links that select a thread in the right pane

### Requirement: User thread list page

The server SHALL serve an HTML page listing all threads for a selected user.

#### Scenario: Drill into user

- **WHEN** a browser navigates to `/report/users/{user_id}`
- **THEN** the server SHALL render a table of threads for that user with `run_count` and last activity
- **AND** each thread row SHALL link to the thread detail page

### Requirement: Thread detail page with agent records

The server SHALL serve an HTML page showing all agent/LLM runs recorded in a thread.

#### Scenario: Inspect thread runs

- **WHEN** a browser navigates to `/report/threads/{thread_id}`
- **THEN** the server SHALL render runs in chronological order with run type, name, status, and timestamps
- **AND** each run SHALL be expandable to show full `inputs.messages` and `outputs`

#### Scenario: Show parent-child hierarchy

- **WHEN** a thread contains runs with `parent_run_id` set
- **THEN** the thread detail page SHALL visually indicate nesting (indentation or tree) so orchestrator vs sub-agent calls are distinguishable

### Requirement: Readable prompt inspection

The thread detail page SHALL present LLM input messages in a human-readable format suitable for debugging (role labels, preserved line breaks, monospace for content).

#### Scenario: View full prompt

- **WHEN** a user expands an LLM run on the thread detail page
- **THEN** the page SHALL display the complete messages array sent to the model without truncation in development mode

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

### Requirement: Admin dark theme aligned with ai-end

The Trace HTML report pages SHALL use a dark color palette and typography consistent with the SEAI ai-end `/admin` dashboard.

#### Scenario: Dark report home

- **WHEN** a browser opens `/report`
- **THEN** the page background SHALL be a dark surface comparable to ai-end Admin (`#0f1419` family)
- **AND** primary text SHALL be light (`#e7ecf3` family) with muted secondary labels
- **AND** accent links SHALL use the Admin accent blue (`#5b9fd4` family)
- **AND** the UI font stack SHALL prefer Segoe UI / system-ui as in ai-end Admin

