# trace-ingestion Specification

## Purpose
TBD - created by archiving change langchain-trace-test-harness. Update Purpose after archive.
## Requirements
### Requirement: Accept run events via HTTP POST

The trace ingestion service SHALL expose an HTTP endpoint that accepts JSON run event payloads from trace clients.

#### Scenario: Successful run event ingestion

- **WHEN** a client POSTs a valid run event to `/api/v1/runs`
- **THEN** the service SHALL return HTTP 201 with the stored run identifier
- **AND** the run event SHALL be persisted for later retrieval

#### Scenario: Reject malformed payload

- **WHEN** a client POSTs an invalid or incomplete run event body
- **THEN** the service SHALL return HTTP 422 with a descriptive error message
- **AND** the payload SHALL NOT be persisted

### Requirement: Store LLM call snapshots

The trace ingestion service SHALL persist LLM call snapshots including input messages, output content, model name, and timestamps.

#### Scenario: Store model call with full messages

- **WHEN** a run event of type `llm` includes an `inputs.messages` array and an `outputs` object
- **THEN** the service SHALL store the complete messages array without truncation in development mode
- **AND** the stored record SHALL include `start_time`, `end_time`, and `status`

### Requirement: Associate runs with user and thread context

The trace ingestion service SHALL index runs by `user_id` and `thread_id` when provided in run metadata.

#### Scenario: Filter runs by thread

- **WHEN** a client GETs `/api/v1/threads/{thread_id}/runs`
- **THEN** the service SHALL return all runs whose metadata contains the matching `thread_id`, ordered by `start_time` ascending

#### Scenario: Propagate metadata on child runs

- **WHEN** a child run event includes `parent_run_id` and metadata with `thread_id` and `user_id`
- **THEN** the service SHALL store the parent-child relationship and metadata fields on the child run record

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

