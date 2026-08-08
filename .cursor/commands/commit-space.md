---
name: /commit-space
id: commit-space
category: Git
description: Commit all git repositories in this workspace (no push)
---

Commit **every git repository** in the current Cursor workspace.

**Read and follow** the personal skill: `git-space` (mode: **commit-space**).

**Do not push.**

Before starting, list which workspace roots are git repos and which have changes.

After all commits, print a summary:

| Repository | Branch | Commit | Notes |
|------------|--------|--------|-------|
