## 1. Data and routing

- [x] 1.1 Add repository helper to load users with nested threads (or reuse existing list methods) for the left pane
- [x] 1.2 Update `GET /report` to accept `thread_id` / `user_id` / `run_id` and render the split-pane home
- [x] 1.3 Redirect `/report/users/{user_id}` and `/report/threads/{thread_id}` to the split home with equivalent query params

## 2. Split UI

- [x] 2.1 Extract styles / split layout into modules so files stay within length limits
- [x] 2.2 Implement left pane overall logs (users → threads, recent activity)
- [x] 2.3 Implement right pane conversation view + expandable runs for the selected thread
- [x] 2.4 Empty state when no thread is selected

## 3. Verification

- [x] 3.1 Add or update tests for `/report` split layout and `?thread_id=` conversation content
- [x] 3.2 Manually smoke-check the admin home in the browser
