# agentsmith-trace-server

FastAPI ingestion service for AgentSmith-Trace run events (SQLite storage, report UI, simulator).

Pair with [`agentsmith-trace-sdk`](https://github.com/MartinChen1973/AgentSmith-Trace) in the SDK repo to capture LangChain LLM calls.

## Quickstart

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/):

```bash
uv sync
cp .env.example .env   # optional
uv run agentsmith-trace-server
```

Server listens on `http://127.0.0.1:9000` by default.

- Swagger UI: `http://127.0.0.1:9000/docs`
- Admin report: `http://127.0.0.1:9000/report` (dark theme aligned with SEAI ai-end `/admin`)
- Simulator: `http://127.0.0.1:9000/simulator`

On Windows (starts the server and opens the admin report):

```bat
run.bat
```

If port `9000` is stuck with a zombie listener (old light UI keeps appearing), `run.bat` automatically falls back to `9001` for that session. A machine reboot clears the stuck port. Hard-refresh with Ctrl+F5 after upgrades.

Server only: `scripts\run-server.bat`

## Development

```bash
uv run pytest
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `AGENTSMITH_TRACE_HOST` | Listen host (default `127.0.0.1`) |
| `AGENTSMITH_TRACE_PORT` | Listen port (default `9000`) |
| `AGENTSMITH_TRACE_DB` | SQLite database path (default `./agentsmith_trace.db`) |
| `AGENTSMITH_TRACE_RELOAD` | `1` = uvicorn auto-reload on code changes (default via `run.bat`); `0` = manual restart |
