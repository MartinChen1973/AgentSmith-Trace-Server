## ADDED Requirements

### Requirement: User overview report page

The server SHALL serve an HTML overview page listing all users and their thread counts.

#### Scenario: Open report home

- **WHEN** a browser navigates to `/` or `/report`
- **THEN** the server SHALL render a page showing each `user_id` with `thread_count` and a link to that user's thread list

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
