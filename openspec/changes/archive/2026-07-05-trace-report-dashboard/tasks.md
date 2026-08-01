## 1. Data layer

- [ ] 1.1 Add `UserSummary` and `ThreadSummary` Pydantic models to `agentsmith_trace_server.models`
- [ ] 1.2 Implement `RunRepository.list_users_summary()` with thread/run counts and last activity
- [ ] 1.3 Implement `RunRepository.list_threads_for_user(user_id)` with run counts and activity timestamps
- [ ] 1.4 Add helper to compute run tree depth from `parent_run_id` for UI indentation

## 2. Report API

- [ ] 2.1 Add `GET /api/v1/report/users` returning user summary list
- [ ] 2.2 Add `GET /api/v1/report/users/{user_id}/threads` returning thread summary list
- [ ] 2.3 Write API tests for aggregation with seeded multi-user/thread data

## 3. Report UI templates

- [ ] 3.1 Add `jinja2` dependency and configure `Jinja2Templates` + static files mount
- [ ] 3.2 Create `base.html` with navigation and shared layout
- [ ] 3.3 Create `report_users.html` — user overview table with thread counts
- [ ] 3.4 Create `report_user_threads.html` — threads for one user with links
- [ ] 3.5 Create `report_thread_detail.html` — run list with expandable messages/outputs and parent-child indent
- [ ] 3.6 Add `static/report.css` for tables, message blocks, and tree indentation

## 4. HTML routes

- [ ] 4.1 Add `GET /` redirect to `/report`
- [ ] 4.2 Add `GET /report` — user overview page
- [ ] 4.3 Add `GET /report/users/{user_id}` — thread list page
- [ ] 4.4 Add `GET /report/threads/{thread_id}` — thread detail page with full run content

## 5. Verification and docs

- [ ] 5.1 Add template render smoke test (TestClient GET `/report` with seeded DB)
- [ ] 5.2 Manually verify navigation: users → threads → run detail with messages visible
- [ ] 5.3 Update `agentsmith-trace-server` README and root README with report UI URL
