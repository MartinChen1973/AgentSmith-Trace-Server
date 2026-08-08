---
name: /push-space
id: push-space
category: Git
description: Commit and push all git repositories in this workspace
---

Commit and push **every git repository** in the current Cursor workspace.

**Read and follow** the personal skill: `git-space` (mode: **push-space**).

1. Commit each repo with changes (same rules as `/commit-space`).
2. Push each repo that has new commits or is ahead of upstream.
3. Do not force-push.

Before starting, list which workspace roots are git repos and which have changes.

After all work, print a summary:

| Repository | Branch | Commit | Push |
|------------|--------|--------|------|
