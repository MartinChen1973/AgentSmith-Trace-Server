## ADDED Requirements

### Requirement: List users with thread counts

The report API SHALL expose an endpoint that returns all distinct `user_id` values with the number of distinct threads per user.

#### Scenario: User summary report

- **WHEN** a client GETs `/api/v1/report/users`
- **THEN** the response SHALL include a list of users, each with `user_id`, `thread_count`, `run_count`, and `last_activity` timestamp

### Requirement: List threads for a user

The report API SHALL expose an endpoint that returns all threads belonging to a given user.

#### Scenario: Threads by user

- **WHEN** a client GETs `/api/v1/report/users/{user_id}/threads`
- **THEN** the response SHALL list distinct `thread_id` values for that user with `run_count`, `first_activity`, and `last_activity`

### Requirement: Thread run detail for dashboard

The report API SHALL reuse or wrap existing thread run listing so the UI can fetch all runs in a thread with parent-child fields and full inputs/outputs.

#### Scenario: Thread runs for UI

- **WHEN** a client GETs `/api/v1/threads/{thread_id}/runs`
- **THEN** each run SHALL include `run_id`, `parent_run_id`, `run_type`, `name`, `status`, `start_time`, `inputs`, `outputs`, and `metadata`

## MODIFIED Requirements

### Requirement: List runs in a trace tree

The trace ingestion service SHALL support retrieval of runs belonging to a single trace or thread, organized by parent-child relationships, for both API consumers and the report UI.

#### Scenario: Retrieve trace tree

- **WHEN** a client GETs `/api/v1/traces/{trace_id}/runs`
- **THEN** the service SHALL return all runs sharing the given `trace_id`
- **AND** each run SHALL include `run_id`, `parent_run_id`, `run_type`, `name`, `status`, `inputs`, and `outputs`

#### Scenario: Retrieve thread runs for inspection

- **WHEN** a client GETs `/api/v1/threads/{thread_id}/runs`
- **THEN** runs SHALL be ordered by `start_time` ascending
- **AND** LLM runs SHALL include full `inputs.messages` for prompt inspection
