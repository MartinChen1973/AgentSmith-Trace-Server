## Why

Traces are ingested into `agentsmith-trace-server`, but there is no way to browse them without raw API calls. Operators need a report-style web UI to see how many users and threads exist, drill into a thread, and inspect what the agent recorded (especially full LLM prompts and outputs).

## What Changes

- Add **report API endpoints** to `agentsmith-trace-server` for user/thread aggregation (user count, threads per user, thread summary).
- Add a **web report UI** served by `agentsmith-trace-server`:
  - **Overview page**: table of users with thread counts (and optional run counts / last activity).
  - **User page**: list of threads for a selected user.
  - **Thread detail page**: chronological list of agent/LLM runs in the thread, expandable to show `inputs.messages` and `outputs` (the debugging snapshot).
- Extend the SQLite repository with aggregation queries (`list_users`, `list_threads_by_user`).
- Serve HTML via FastAPI (Jinja2 templates + minimal CSS); no separate frontend app for MVP.
- Root URL `/` redirects to the report overview.

## Capabilities

### New Capabilities

- `trace-report-api`: Read-only aggregation and navigation APIs backing the dashboard (users, threads, run detail).
- `trace-report-ui`: Server-rendered report pages for user/thread overview and per-thread agent run inspection.

### Modified Capabilities

- `trace-ingestion`: Extend ingestion service with read/query endpoints required by the dashboard (user and thread listing).

## Impact

- Package: `packages/agentsmith-trace-server` (API, DB layer, templates, static assets)
- New dependencies: `jinja2` (templates)
- No changes to `agentsmith-trace-sdk` or test-harness required
- Existing JSON APIs (`/api/v1/threads/{id}/runs`) remain; new routes are additive
