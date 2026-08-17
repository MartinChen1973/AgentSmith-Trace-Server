"""Shared CSS for AgentSmith-Trace report HTML pages (ai-end Admin dark theme)."""

from __future__ import annotations

COMMON_STYLES = """
    :root {
      --bg: #0f1419;
      --surface: #1a2332;
      --border: #2d3a4d;
      --text: #e7ecf3;
      --muted: #8b9cae;
      --accent: #5b9fd4;
      --ok: #3d9e6f;
      --warn: #c9a227;
      --err: #d85c5c;
      --chip-bg: #243044;
      --user-bg: #1e3a54;
      --assistant-bg: #243044;
      --system-bg: #3a2f1e;
      --code-bg: #0a0e14;
      --font: "Segoe UI", system-ui, sans-serif;
      --mono: ui-monospace, "Cascadia Code", Consolas, monospace;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: var(--font);
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      min-height: 100vh;
    }
    body.single {
      margin: 0 auto;
      max-width: 1100px;
      padding: 1.25rem 1.5rem 2rem;
    }
    h1 {
      margin: 0;
      font-size: 1.15rem;
      font-weight: 600;
      color: var(--text);
    }
    h2 {
      font-size: 0.92rem;
      font-weight: 600;
      margin: 0 0 0.5rem;
      color: var(--muted);
    }
    .sub {
      color: var(--muted);
      margin: 0.25rem 0 0;
      font-size: 0.85rem;
    }
    table { border-collapse: collapse; width: 100%; }
    th, td {
      border: 1px solid var(--border);
      padding: 0.5rem 0.75rem;
      text-align: left;
    }
    th {
      background: var(--chip-bg);
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-weight: 600;
    }
    td { background: rgba(26, 35, 50, 0.45); }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    code {
      font-family: var(--mono);
      background: var(--chip-bg);
      color: var(--text);
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
      font-size: 0.85em;
      border: 1px solid var(--border);
    }
    .crumbs { color: var(--muted); margin-bottom: 1rem; font-size: 0.85rem; }
    .session {
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 0.85rem 1rem;
      border-radius: 8px;
      margin-bottom: 1rem;
      font-size: 0.9rem;
    }
    .run {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.5rem 0.75rem;
      margin: 0.5rem 0;
      background: rgba(26, 35, 50, 0.55);
    }
    .pill {
      background: rgba(91, 159, 212, 0.18);
      color: var(--accent);
      border: 1px solid rgba(91, 159, 212, 0.35);
      padding: 0.1rem 0.45rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.15rem;
      flex-shrink: 0;
    }
    .pill-emoji {
      font-size: 0.85rem;
      line-height: 1;
    }
    .muted { color: var(--muted); font-size: 0.85rem; margin-left: 0.5rem; }
    .msg { margin: 0.5rem 0; }
    .role { font-weight: 600; color: var(--muted); font-size: 0.78rem; text-transform: uppercase; }
    pre.content {
      white-space: pre-wrap;
      background: var(--code-bg);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 0.75rem;
      border-radius: 6px;
      overflow-x: auto;
      font-size: 0.82rem;
      font-family: var(--mono);
    }
    .panel h4 {
      margin: 0.75rem 0 0.35rem;
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .panel .actions { margin-top: 0.5rem; font-size: 0.85rem; }
    summary { cursor: pointer; color: var(--text); }
    .meta-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 0.35rem 1rem;
      margin: 0.5rem 0;
      font-size: 0.85rem;
    }
    .meta-grid dt { color: var(--muted); }
    .meta-grid dd { margin: 0; }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--border);
      background: var(--surface);
    }
    .topbar nav {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }
    .topbar nav a {
      color: var(--accent);
      font-size: 0.9rem;
    }
    .split {
      display: grid;
      grid-template-columns: minmax(280px, 34%) 1fr;
      height: calc(100vh - 4.75rem);
      min-height: 420px;
    }
    .pane {
      overflow: auto;
      padding: 1.25rem 1.5rem;
      background: var(--bg);
    }
    .pane-left { border-right: 1px solid var(--border); }
    .user-block { margin-bottom: 1.25rem; }
    .user-block h2 {
      margin: 0 0 0.5rem;
      font-size: 0.78rem;
      color: var(--muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .thread-list { list-style: none; margin: 0; padding: 0; }
    .thread-list li { margin: 0 0 0.35rem; }
    .thread-link {
      display: block;
      padding: 0.55rem 0.65rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: inherit;
      background: rgba(26, 35, 50, 0.55);
    }
    .thread-link:hover {
      border-color: rgba(91, 159, 212, 0.55);
      background: rgba(26, 48, 72, 0.82);
      text-decoration: none;
    }
    .thread-link.active {
      border-color: var(--accent);
      background: rgba(36, 64, 96, 0.9);
      box-shadow: inset 3px 0 0 var(--accent);
    }
    .thread-id {
      font-family: var(--mono);
      font-size: 0.78rem;
      word-break: break-all;
      color: var(--text);
    }
    .thread-meta { color: var(--muted); font-size: 0.72rem; margin-top: 0.2rem; }
    .empty {
      color: var(--muted);
      border: 1px dashed var(--border);
      border-radius: 8px;
      padding: 2rem 1rem;
      text-align: center;
      background: rgba(26, 35, 50, 0.35);
      font-size: 0.9rem;
    }
    .chat-panel { margin: 1rem 0; }
    .chat-toolbar {
      display: flex;
      justify-content: flex-end;
      gap: 0.45rem;
      margin-bottom: 0.45rem;
    }
    .chat-toolbar button {
      font-family: var(--font);
      font-size: 0.72rem;
      padding: 0.2rem 0.55rem;
      border-radius: 5px;
      border: 1px solid var(--border);
      background: var(--chip-bg);
      color: var(--muted);
      cursor: pointer;
      line-height: 1.35;
    }
    .chat-toolbar button:hover {
      color: var(--text);
      border-color: rgba(91, 159, 212, 0.45);
      background: rgba(36, 64, 96, 0.35);
    }
    .chat { display: flex; flex-direction: column; gap: 0.45rem; margin: 0; }
    .chat-row {
      display: flex;
      width: 100%;
      box-sizing: border-box;
    }
    .chat-row-user { justify-content: flex-end; }
    .chat-row-assistant,
    .chat-row-system,
    .chat-row-tool { justify-content: flex-start; }
    .chat-block {
      display: flex;
      align-items: flex-start;
      gap: 0.4rem;
      width: fit-content;
      max-width: min(92%, 720px);
    }
    .chat-avatar {
      flex-shrink: 0;
      width: 1.65rem;
      height: 1.65rem;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--border);
      background: var(--chip-bg);
      color: var(--muted);
    }
    .chat-avatar-user {
      background: var(--user-bg);
      color: var(--accent);
      border-color: rgba(91, 159, 212, 0.45);
    }
    .chat-avatar-assistant {
      background: rgba(36, 64, 96, 0.85);
      color: var(--accent);
      border-color: rgba(91, 159, 212, 0.45);
    }
    .chat-avatar-system {
      background: var(--system-bg);
      color: var(--warn);
      border-color: rgba(201, 162, 39, 0.45);
    }
    .chat-avatar-tool {
      background: rgba(58, 47, 30, 0.85);
      color: var(--warn);
      border-color: rgba(201, 162, 39, 0.45);
    }
    .avatar-emoji {
      font-size: 1.05rem;
      line-height: 1;
      display: block;
    }
    .avatar-emoji {
      font-size: 0.9rem;
      line-height: 1;
      display: block;
    }
    .avatar-icon-wrap,
    .tool-inline-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .tool-inline-icon {
      margin-right: 0.45rem;
      vertical-align: middle;
    }
    .tool-inline-svg {
      width: 1.1rem;
      height: 1.1rem;
      fill: currentColor;
      display: block;
    }
    .avatar-icon-wrap .tool-inline-svg {
      width: 0.95rem;
      height: 0.95rem;
    }
    .tool-summary {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      color: var(--muted);
    }
    .tool-inline-write_todos { color: var(--accent); }
    .tool-inline-read_file { color: var(--accent); }
    .tool-inline-write_file,
    .tool-inline-edit_file { color: var(--warn); }
    .tool-inline-skill { color: var(--ok); }
    .todo-list {
      list-style: none;
      margin: 0.5rem 0 0;
      padding: 0;
      border-top: 1px solid var(--border);
    }
    .todo-item {
      display: flex;
      gap: 0.45rem;
      align-items: flex-start;
      padding: 0.35rem 0;
      font-size: 0.8rem;
      color: var(--text);
      border-bottom: 1px solid rgba(45, 58, 77, 0.55);
    }
    .todo-list.compact {
      margin: 0.2rem 0 0;
      border-top: none;
      padding-left: 0;
    }
    .todo-list.compact .todo-item {
      padding: 0.12rem 0;
      font-size: 0.74rem;
      border-bottom: none;
      gap: 0.3rem;
    }
    .todo-list.compact .todo-status {
      font-size: 0.62rem;
      padding: 0 0.3rem;
    }
    .todo-list-full .todo-item span {
      white-space: normal;
      word-break: break-word;
    }
    .bubble-todos,
    .stack-summary-todos {
      display: block;
      margin-top: 0.2rem;
    }
    .stack-summary-todos .todo-list {
      border-top: 1px solid rgba(45, 58, 77, 0.55);
      margin-top: 0.15rem;
      padding-top: 0.15rem;
    }
    .bubble.compact:not(.is-expanded) .bubble-todos {
      display: block;
    }
    .todo-item:last-child { border-bottom: none; }
    .todo-status {
      flex-shrink: 0;
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--muted);
      background: var(--chip-bg);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.05rem 0.4rem;
    }
    .todo-plan-panel,
    .todo-outcome-panel {
      margin: 0 0 1rem;
      padding: 0.75rem 0.9rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: rgba(12, 18, 28, 0.55);
    }
    .todo-plan-panel h3,
    .todo-outcome-panel h3 {
      margin: 0 0 0.35rem;
      font-size: 0.95rem;
    }
    .todo-plan-owner,
    .todo-outcome-owner {
      margin-top: 0.65rem;
    }
    .todo-plan-owner-title,
    .todo-outcome-owner-title {
      margin: 0 0 0.25rem;
      font-size: 0.82rem;
      color: var(--accent);
    }
    .todo-outcome-list {
      list-style: none;
      margin: 0.25rem 0 0;
      padding: 0;
    }
    .todo-outcome-item {
      display: flex;
      gap: 0.45rem;
      align-items: flex-start;
      padding: 0.28rem 0;
      font-size: 0.78rem;
      border-bottom: 1px solid rgba(45, 58, 77, 0.45);
    }
    .todo-outcome-item:last-child { border-bottom: none; }
    .todo-outcome {
      flex-shrink: 0;
      font-size: 0.62rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      border-radius: 999px;
      padding: 0.05rem 0.4rem;
      border: 1px solid var(--border);
    }
    .todo-outcome-done {
      color: var(--ok);
      border-color: rgba(61, 158, 111, 0.45);
      background: rgba(61, 158, 111, 0.12);
    }
    .todo-outcome-not_done {
      color: var(--warn);
      border-color: rgba(212, 153, 59, 0.45);
      background: rgba(212, 153, 59, 0.12);
    }
    .todo-outcome-added,
    .todo-outcome-removed,
    .todo-outcome-revised {
      color: var(--muted);
      background: var(--chip-bg);
    }
    .todo-outcome-detail {
      font-size: 0.72rem;
    }
    .chat-avatar-skill {
      background: rgba(61, 158, 111, 0.22);
      border-color: rgba(61, 158, 111, 0.5);
    }
    .chat-avatar-read_file {
      background: rgba(91, 159, 212, 0.2);
      border-color: rgba(91, 159, 212, 0.45);
    }
    .chat-avatar-write_file {
      background: rgba(201, 162, 39, 0.2);
      border-color: rgba(201, 162, 39, 0.45);
    }
    .chat-avatar-edit_file {
      background: rgba(201, 162, 39, 0.16);
      border-color: rgba(201, 162, 39, 0.4);
    }
    .chat-avatar-write_todos {
      background: rgba(91, 159, 212, 0.16);
      border-color: rgba(91, 159, 212, 0.4);
    }
    .chat-avatar-task {
      background: rgba(139, 108, 212, 0.22);
      border-color: rgba(139, 108, 212, 0.45);
    }
    .bubble.tool.skill {
      border-color: rgba(61, 158, 111, 0.45);
      background: rgba(61, 158, 111, 0.12);
    }
    .bubble.tool.read_file {
      border-color: rgba(91, 159, 212, 0.4);
      background: rgba(36, 64, 96, 0.45);
    }
    .bubble.tool.write_file,
    .bubble.tool.edit_file {
      border-color: rgba(201, 162, 39, 0.4);
      background: rgba(58, 47, 30, 0.5);
    }
    .bubble.tool.write_todos {
      border-color: rgba(91, 159, 212, 0.35);
      background: rgba(36, 64, 96, 0.35);
    }
    .bubble.tool.task {
      border-color: rgba(139, 108, 212, 0.4);
      background: rgba(68, 52, 108, 0.35);
    }
    .avatar-icon {
      width: 1.1rem;
      height: 1.1rem;
      fill: currentColor;
      display: block;
    }
    .bubble {
      flex: 1 1 auto;
      min-width: 0;
      padding: 0.65rem 0.85rem;
      border-radius: 10px;
      border: 1px solid var(--border);
      text-align: left;
    }
    .bubble.compact {
      padding: 0.28rem 0.55rem;
      border-radius: 7px;
      line-height: 1.35;
    }
    .bubble.compact.bubble-expandable {
      cursor: pointer;
    }
    .bubble.compact.bubble-expandable:hover {
      border-color: rgba(91, 159, 212, 0.45);
    }
    .bubble-main {
      display: flex;
      flex-wrap: nowrap;
      align-items: baseline;
      gap: 0.3rem 0.45rem;
      font-size: 0.8rem;
      line-height: 1.35;
      overflow: hidden;
      max-width: 100%;
    }
    .bubble-main .speaker {
      font-size: 0.68rem;
      font-weight: 600;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      flex-shrink: 0;
    }
    .bubble-main .bubble-text {
      color: var(--text);
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1 1 auto;
    }
    .bubble-main .bubble-text-preview {
      white-space: pre-wrap;
      text-overflow: unset;
      overflow: hidden;
      line-height: 1.35;
      flex: 1 1 100%;
    }
    .bubble.compact:not(.is-expanded) .bubble-text-full {
      display: none;
    }
    .bubble.compact.is-expanded .bubble-text-preview {
      display: none;
    }
    .bubble.compact.is-expanded .bubble-main {
      overflow: visible;
      flex-wrap: wrap;
      align-items: flex-start;
    }
    .bubble.compact.is-expanded .bubble-main .bubble-text-full {
      white-space: pre-wrap;
      overflow: visible;
      text-overflow: unset;
      word-break: break-word;
      flex: 1 1 100%;
    }
    .bubble.compact.is-expanded .bubble-main .bubble-param {
      max-width: 100%;
      white-space: pre-wrap;
      word-break: break-word;
      overflow: visible;
      text-overflow: unset;
    }
    .bubble-main .bubble-param {
      font-family: var(--mono);
      font-size: 0.74rem;
      color: var(--accent);
      background: rgba(26, 35, 50, 0.55);
      border: 1px solid rgba(91, 159, 212, 0.25);
      padding: 0.02rem 0.3rem;
      border-radius: 3px;
      flex-shrink: 0;
      max-width: 45%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .bubble-meta {
      margin-top: 0.12rem;
      font-size: 0.66rem;
      color: var(--muted);
      line-height: 1.2;
      font-family: var(--mono);
    }
    .bubble.user {
      background: var(--user-bg);
      border-color: rgba(91, 159, 212, 0.35);
    }
    .bubble.assistant {
      background: var(--assistant-bg);
    }
    .bubble.system {
      background: var(--system-bg);
      border-color: rgba(201, 162, 39, 0.35);
    }
    .bubble.tool {
      background: rgba(58, 47, 30, 0.55);
      border-color: rgba(201, 162, 39, 0.35);
      padding: 0.28rem 0.55rem;
    }
    .bubble .body {
      white-space: pre-wrap;
      font-size: 0.9rem;
      line-height: 1.45;
      color: var(--text);
    }
    .activity-chip {
      font-size: 0.78rem;
      color: var(--muted);
      line-height: 1.35;
    }
    .stack-legend { margin: 0 0 0.75rem; }
    .stack-frame > summary.stack-summary {
      display: block;
      min-width: 0;
    }
    .stack-summary-row {
      display: flex;
      align-items: center;
      gap: 0.35rem 0.5rem;
      min-width: 0;
      max-width: 100%;
    }
    .stack-summary-head {
      flex-wrap: nowrap;
    }
    .stack-summary-leading {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      min-width: 0;
      flex: 1 1 auto;
    }
    .stack-summary-leading .stack-title {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .stack-summary-end {
      display: flex;
      align-items: center;
      gap: 0.35rem 0.45rem;
      flex-shrink: 0;
      margin-left: auto;
    }
    .stack-summary-end .muted {
      margin-left: 0;
    }
    .stack-summary-param {
      margin-top: 0.18rem;
      padding-right: 0.15rem;
    }
    .stack-param-line {
      display: block;
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;
      font-family: var(--mono);
      font-size: 0.74rem;
      color: var(--accent);
      overflow: hidden;
      min-width: 0;
      white-space: pre-wrap;
      line-height: 1.35;
    }
    .stack-param-line.stack-param-multiline {
      white-space: pre-wrap;
    }
    .stack-param-line:not(.stack-param-multiline) {
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .stack-param {
      font-family: var(--mono);
      font-size: 0.74rem;
      color: var(--accent);
      background: rgba(26, 35, 50, 0.55);
      border: 1px solid rgba(91, 159, 212, 0.25);
      padding: 0.02rem 0.35rem;
      border-radius: 3px;
      max-width: 42%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      vertical-align: middle;
    }
    .status-merge {
      display: inline-flex;
      align-items: center;
      gap: 0.12rem;
      flex-shrink: 0;
      vertical-align: middle;
    }
    .status-merge-arrow {
      font-size: 0.62rem;
      color: var(--muted);
      line-height: 1;
    }
    .status-pill {
      font-size: 0.62rem;
      font-weight: 600;
      letter-spacing: 0.03em;
      text-transform: lowercase;
      padding: 0.04rem 0.38rem;
      border-radius: 3px;
      border: 1px solid var(--border);
      line-height: 1.25;
      flex-shrink: 0;
    }
    .status-pill.status-pending {
      color: var(--warn);
      background: rgba(201, 162, 39, 0.16);
      border-color: rgba(201, 162, 39, 0.45);
    }
    .status-pill.status-success {
      color: var(--ok);
      background: rgba(61, 158, 111, 0.16);
      border-color: rgba(61, 158, 111, 0.45);
    }
    .status-pill.status-error {
      color: var(--err);
      background: rgba(216, 92, 92, 0.14);
      border-color: rgba(216, 92, 92, 0.45);
    }
    .has-tip {
      cursor: help;
    }
    .stack-time {
      font-family: var(--mono);
      font-size: 0.72rem;
    }
    .call-stack {
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .call-stack .call-stack {
      margin: 0.15rem 0 0.35rem 1.1rem;
      padding-left: 0.75rem;
      border-left: 1px solid var(--border);
    }
    .stack-node { margin: 0.35rem 0; }
    .stack-frame { margin: 0; }
    .stack-root > .stack-frame {
      border-color: rgba(91, 159, 212, 0.55);
      background: rgba(36, 64, 96, 0.55);
    }
    .stack-class > .stack-frame {
      border-color: rgba(201, 162, 39, 0.55);
      background: rgba(58, 47, 30, 0.55);
    }
    .stack-class > .stack-frame .stack-title {
      font-size: 1.02em;
      letter-spacing: 0.01em;
    }
    .stack-skill > .stack-frame {
      border-color: rgba(61, 158, 111, 0.55);
    }
    .stack-skill-ref > .stack-frame {
      border-style: dashed;
      border-color: rgba(61, 158, 111, 0.45);
      background: rgba(26, 35, 50, 0.35);
    }
    .stack-method > .stack-frame {
      background: rgba(26, 35, 50, 0.4);
    }
    .pill-deep-agent {
      background: rgba(91, 159, 212, 0.22);
      color: var(--accent);
    }
    .pill-class {
      background: rgba(201, 162, 39, 0.2);
      color: var(--warn);
      border-color: rgba(201, 162, 39, 0.4);
    }
    .pill-skill {
      background: rgba(61, 158, 111, 0.2);
      color: var(--ok);
      border-color: rgba(61, 158, 111, 0.4);
    }
    .pill-ref {
      background: rgba(61, 158, 111, 0.12);
      color: var(--ok);
      border-color: rgba(61, 158, 111, 0.35);
      border-style: dashed;
    }
    .pill-method {
      background: var(--chip-bg);
      color: var(--muted);
      border-color: var(--border);
    }
    @media (max-width: 900px) {
      .split { grid-template-columns: 1fr; height: auto; }
      .pane-left {
        border-right: none;
        border-bottom: 1px solid var(--border);
        max-height: 40vh;
      }
    }
"""

REPORT_CHAT_SCRIPT = """
(function () {
  function chatBubbles(panel) {
    return panel.querySelectorAll(".bubble.compact.bubble-expandable");
  }
  function toggleBubble(bubble) {
    bubble.classList.toggle("is-expanded");
  }
  function setAllExpanded(panel, expanded) {
    chatBubbles(panel).forEach(function (bubble) {
      if (expanded) {
        bubble.classList.add("is-expanded");
      } else {
        bubble.classList.remove("is-expanded");
      }
    });
  }
  document.addEventListener("click", function (event) {
    var expandBtn = event.target.closest("[data-chat-expand-all]");
    if (expandBtn) {
      event.preventDefault();
      var panel = expandBtn.closest(".chat-panel");
      if (panel) {
        setAllExpanded(panel, true);
      }
      return;
    }
    var collapseBtn = event.target.closest("[data-chat-collapse-all]");
    if (collapseBtn) {
      event.preventDefault();
      var panelCollapse = collapseBtn.closest(".chat-panel");
      if (panelCollapse) {
        setAllExpanded(panelCollapse, false);
      }
      return;
    }
    var bubble = event.target.closest(".bubble.compact.bubble-expandable");
    if (!bubble || !bubble.closest(".chat")) {
      return;
    }
    toggleBubble(bubble);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }
    var bubble = event.target.closest(".bubble.compact.bubble-expandable");
    if (!bubble || !bubble.closest(".chat")) {
      return;
    }
    event.preventDefault();
    toggleBubble(bubble);
  });
})();
"""
