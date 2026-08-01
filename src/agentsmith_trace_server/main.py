from __future__ import annotations

import os

import uvicorn

from agentsmith_trace_server.api import create_app

app = create_app()


def cli() -> None:
    host = os.environ.get("AGENTSMITH_TRACE_HOST", "127.0.0.1")
    port = int(os.environ.get("AGENTSMITH_TRACE_PORT", "9000"))
    reload = os.environ.get("AGENTSMITH_TRACE_RELOAD", "1") != "0"

    if reload:
        uvicorn.run(
            "agentsmith_trace_server.main:app",
            host=host,
            port=port,
            reload=True,
        )
    else:
        uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
