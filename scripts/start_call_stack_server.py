"""Start Trace Server with the local src package (call-stack UI)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from agentsmith_trace_server.report_panels import render_runs_list
import inspect

assert "call-stack" in inspect.getsource(render_runs_list), "old render_runs_list loaded"

os.environ.setdefault("AGENTSMITH_TRACE_HOST", "127.0.0.1")
os.environ.setdefault("AGENTSMITH_TRACE_PORT", "9010")

import uvicorn
from agentsmith_trace_server.api import app

host = os.environ["AGENTSMITH_TRACE_HOST"]
port = int(os.environ["AGENTSMITH_TRACE_PORT"])
print(f"starting call-stack Trace Server on http://{host}:{port}", flush=True)
uvicorn.run(app, host=host, port=port)
