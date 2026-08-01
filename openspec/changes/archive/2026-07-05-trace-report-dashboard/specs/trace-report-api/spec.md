## ADDED Requirements

### Requirement: User aggregation endpoint

The report API SHALL provide a JSON endpoint for user-level statistics used by the UI and external tools.

#### Scenario: JSON user report

- **WHEN** a client GETs `/api/v1/report/users`
- **THEN** the response SHALL be JSON with shape `{ "users": [ { "user_id", "thread_count", "run_count", "last_activity" } ], "count" }`

### Requirement: Per-user thread aggregation endpoint

The report API SHALL provide a JSON endpoint listing threads for one user.

#### Scenario: JSON thread list

- **WHEN** a client GETs `/api/v1/report/users/{user_id}/threads`
- **THEN** the response SHALL be JSON with shape `{ "threads": [ { "thread_id", "run_count", "first_activity", "last_activity" } ], "count" }`

### Requirement: Report API matches UI data needs

Report API responses SHALL be derived from the same repository queries used by HTML pages so API and UI stay consistent.

#### Scenario: Consistent counts

- **WHEN** the overview page shows a user with `thread_count` of 3
- **THEN** `GET /api/v1/report/users` SHALL report `thread_count` of 3 for the same `user_id`
