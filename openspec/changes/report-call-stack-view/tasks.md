## 1. Call-stack tree builder

- [x] 1.1 Add tree-build helper (explicit `parent_run_id` + same-`trace_id` heuristic attach)
- [x] 1.2 Classify node roles: root, class (subagent), method, skill, skill-ref
- [x] 1.3 Add unit tests for tree build and skill-ref detection

## 2. Report rendering and styles

- [x] 2.1 Replace flat `render_runs_list` with nested call-stack HTML
- [x] 2.2 Add CSS for root/class/method/skill/skill-ref emphasis
- [x] 2.3 Keep expandable panels and optional open_run_id behavior

## 3. Verification

- [x] 3.1 Run Trace Server unit tests for report panels / tree
- [x] 3.2 Smoke-check `/report` against an existing thread if server is up
