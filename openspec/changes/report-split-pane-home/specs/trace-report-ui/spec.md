## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: User overview report page

The server SHALL serve an HTML overview page as the left pane of `/report`, listing users and their threads with activity counts.

#### Scenario: Open report home

- **WHEN** a browser navigates to `/` or `/report`
- **THEN** the server SHALL render overall activity in the left pane, including each `user_id` with thread entries and links that select a thread in the right pane
