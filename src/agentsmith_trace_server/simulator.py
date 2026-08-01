from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, HTTPException
from pydantic import BaseModel, Field


class SimulatorRunRequest(BaseModel):
    user_id: str = "usr_demo"
    thread_id: str | None = None


class SimulatorRunResponse(BaseModel):
    status: str
    user_id: str
    thread_id: str
    message: str


class SimulatorStatusResponse(BaseModel):
    running: bool
    last_user_id: str | None = None
    last_thread_id: str | None = None
    last_error: str | None = None


_state = {
    "running": False,
    "last_user_id": None,
    "last_thread_id": None,
    "last_error": None,
}


def _merge_dotenv(env: dict[str, str], env_file: Path) -> None:
    """Merge .env into env; later lines override earlier ones."""
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            env[key] = value


def project_root() -> Path:
    env_root = os.environ.get("AGENTSMITH_PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path.cwd().resolve()


def simulator_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <title>AgentSmith-Trace Simulator</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; max-width: 720px; }
    h1 { margin-bottom: 0.25rem; }
    p.sub { color: #555; }
    button {
      font-size: 1.1rem; padding: 0.75rem 1.5rem; cursor: pointer;
      background: #0969da; color: #fff; border: none; border-radius: 8px;
    }
    button:disabled { background: #94a3b8; cursor: not-allowed; }
    #status { margin-top: 1.25rem; padding: 1rem; background: #f6f8fa; border-radius: 8px; }
    a { color: #0969da; }
    code { background: #eef; padding: 0.1rem 0.35rem; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Test Simulator</h1>
  <p class="sub">Run the LangChain test harness (orchestrator + 2 sub-agents). Traces are sent to this server.</p>
  <p>
    <label>User ID <input id="userId" value="usr_demo" /></label>
    &nbsp;
    <label>Thread ID <input id="threadId" placeholder="auto" /></label>
  </p>
  <button id="runBtn" onclick="runTest()">Run sample test</button>
  <div id="status">Ready.</div>
  <p style="margin-top:2rem">
    <a href="/report">Admin report</a> · <a href="/docs">Swagger UI</a>
  </p>
  <script>
    async function runTest() {
      const btn = document.getElementById('runBtn');
      const status = document.getElementById('status');
      const user_id = document.getElementById('userId').value || 'usr_demo';
      const thread_id = document.getElementById('threadId').value || null;
      btn.disabled = true;
      status.textContent = 'Starting test run...';
      try {
        const res = await fetch('/api/v1/simulator/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id, thread_id }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || res.statusText);
        status.innerHTML = 'Running in background. thread: <code>' + data.thread_id +
          '</code><br>Refresh <a href="/report">report</a> in ~30-60s to see traces.';
        pollStatus();
      } catch (e) {
        status.textContent = 'Error: ' + e.message;
        btn.disabled = false;
      }
    }
    async function pollStatus() {
      const btn = document.getElementById('runBtn');
      const status = document.getElementById('status');
      const res = await fetch('/api/v1/simulator/status');
      const data = await res.json();
      if (data.running) {
        setTimeout(pollStatus, 2000);
        return;
      }
      btn.disabled = false;
      if (data.last_error) {
        status.textContent = 'Failed: ' + data.last_error;
      } else if (data.last_thread_id) {
        status.innerHTML = 'Done. View thread <code>' + data.last_thread_id +
          '</code> on <a href="/report">report</a> or ' +
          '<a href="/api/v1/threads/' + data.last_thread_id + '/runs">JSON API</a>.';
      }
    }
  </script>
</body>
</html>"""


def _run_harness_subprocess(user_id: str, thread_id: str) -> None:
    global _state
    _state["running"] = True
    _state["last_error"] = None
    _state["last_user_id"] = user_id
    _state["last_thread_id"] = thread_id
    root = project_root()
    env = os.environ.copy()
    _merge_dotenv(env, root / ".env")
    env["AGENTSMITH_TRACE_URL"] = env.get(
        "AGENTSMITH_TRACE_URL", "http://127.0.0.1:9000"
    )
    env["USER_ID"] = user_id
    env["THREAD_ID"] = thread_id
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "test_harness",
                "run",
                "--user-id",
                user_id,
                "--thread-id",
                thread_id,
            ],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "harness failed").strip()
            _state["last_error"] = err[-2000:]
    except Exception as exc:
        _state["last_error"] = str(exc)
    finally:
        _state["running"] = False


def start_simulator_run(
    background_tasks: BackgroundTasks,
    body: SimulatorRunRequest,
) -> SimulatorRunResponse:
    if _state["running"]:
        raise HTTPException(status_code=409, detail="A test run is already in progress")

    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY is not set. Copy .env.example to .env and add your key.",
        )

    where_uv = subprocess.run(
        ["where", "uv"] if sys.platform == "win32" else ["which", "uv"],
        capture_output=True,
        text=True,
    )
    if where_uv.returncode != 0:
        raise HTTPException(status_code=500, detail="uv is not installed or not on PATH")

    thread_id = body.thread_id or f"thread_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
    background_tasks.add_task(_run_harness_subprocess, body.user_id, thread_id)
    return SimulatorRunResponse(
        status="started",
        user_id=body.user_id,
        thread_id=thread_id,
        message="Test harness started in background. Check /report when complete.",
    )


def get_simulator_status() -> SimulatorStatusResponse:
    return SimulatorStatusResponse(
        running=_state["running"],
        last_user_id=_state["last_user_id"],
        last_thread_id=_state["last_thread_id"],
        last_error=_state["last_error"],
    )
