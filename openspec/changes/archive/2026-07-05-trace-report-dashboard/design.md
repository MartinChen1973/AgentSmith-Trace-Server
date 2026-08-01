## Context

`agentsmith-trace-server` ingests run events with `metadata.user_id` and `metadata.thread_id`. JSON APIs exist for single-thread run listing, but operators cannot answer "how many users / threads do we have?" or inspect prompts without `curl`.

The primary debugging workflow (from project exploration) is: find a thread → open an LLM run → read full `inputs.messages` + `outputs`.

## Goals / Non-Goals

**Goals:**

- Server-rendered report UI at `/report`
- User overview → user threads → thread run detail navigation
- Show LLM snapshots (messages + outputs) on thread detail page
- Parent-child visual hierarchy for orchestrator / sub-agent runs
- JSON report APIs mirroring UI data
- SQLite aggregation queries (no new database)

**Non-Goals:**

- Authentication / multi-tenant access control (future)
- LLM replay playground (future)
- Separate React/SPA frontend
- Real-time live updates / WebSocket
- Editing or deleting runs from UI

## Decisions

### 1. Server-rendered HTML (Jinja2)

FastAPI + Jinja2Templates embedded in `agentsmith-trace-server`.

**Rationale:** Single deployable unit; matches MVP scope; no build toolchain.

**Alternatives:** React SPA — rejected for MVP complexity.

### 2. Page flow

```
/  →  /report                    (user overview)
/report/users/{user_id}         (threads for user)
/report/threads/{thread_id}     (runs in thread, expandable detail)
```

Breadcrumb navigation on each page.

### 3. SQLite aggregation

New `RunRepository` methods:

```sql
-- Users summary
SELECT
  json_extract(metadata_json, '$.user_id') AS user_id,
  COUNT(DISTINCT json_extract(metadata_json, '$.thread_id')) AS thread_count,
  COUNT(*) AS run_count,
  MAX(start_time) AS last_activity
FROM runs
WHERE json_extract(metadata_json, '$.user_id') IS NOT NULL
GROUP BY user_id;

-- Threads for user (similar GROUP BY thread_id with user filter)
```

Runs without `user_id` in metadata are excluded from user reports (or grouped as `_unknown` — use `_unknown` for null user_id).

### 4. Thread detail layout

| Column / section | Content |
|------------------|---------|
| Run header | `name`, `run_type`, `status`, time, latency |
| Expandable body | `inputs.messages` as stacked message cards (role + content) |
| Output | `outputs.content` or error |
| Tree | Indent by `parent_run_id` depth |

### 5. API routes (additive)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/report/users` | User summary JSON |
| GET | `/api/v1/report/users/{user_id}/threads` | Threads JSON |
| GET | `/api/v1/threads/{thread_id}/runs` | Existing — used by detail page |

HTML routes call repository directly (same queries as API).

### 6. Static assets

Minimal CSS in `agentsmith_trace_server/static/report.css` — clean table layout, monospace message blocks, indent classes for tree depth.

### 7. Package layout

```
agentsmith_trace_server/
├── api.py              # add report routes
├── db.py               # aggregation queries
├── report.py           # HTML route handlers (optional module)
├── models.py           # UserSummary, ThreadSummary response models
├── templates/
│   ├── base.html
│   ├── report_users.html
│   ├── report_user_threads.html
│   └── report_thread_detail.html
└── static/
    └── report.css
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Large prompts slow page render | No truncation in dev; add collapse-by-default; paginate runs if >50 |
| SQLite JSON aggregation performance | Acceptable for dev volumes; index on metadata fields already exists |
| XSS from stored prompt content | Jinja2 auto-escape enabled; render message content as escaped text |

## Migration Plan

1. Add repository aggregation methods + Pydantic models
2. Add JSON report API routes
3. Add templates + HTML routes
4. Add tests for API aggregation and one template render smoke test
5. Update README with `/report` URL

No breaking changes to ingestion API.

## Open Questions

- Show `_unknown` user for runs missing `user_id`? (Default: yes, grouped as `_unknown`.)
- Group runs by `trace_id` within thread view? (Default: flat chronological list with parent indent; trace_id shown in metadata.)
