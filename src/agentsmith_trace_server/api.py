from __future__ import annotations

import os
from uuid import UUID

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from agentsmith_trace_server.db import RunRepository, default_db_path
from agentsmith_trace_server.models import (
    RunEvent,
    RunEventResponse,
    RunListResponse,
    ThreadListResponse,
)
from agentsmith_trace_server.report_panels import report_home_href
from agentsmith_trace_server.report_view import (
    report_home_html,
    run_detail_html,
)
from agentsmith_trace_server.simulator import (
    SimulatorRunRequest,
    SimulatorRunResponse,
    SimulatorStatusResponse,
    get_simulator_status,
    simulator_html,
    start_simulator_run,
)

META_USER_ID = "user_id"


def create_app(db_path: str | None = None) -> FastAPI:
    repo = RunRepository(db_path or default_db_path())
    app = FastAPI(title="AgentSmith-Trace", version="0.1.0")

    @app.post("/api/v1/runs", response_model=RunEventResponse, status_code=201)
    def ingest_run(event: RunEvent) -> RunEventResponse:
        repo.upsert(event)
        return RunEventResponse(run_id=event.run_id)

    @app.get("/api/v1/runs/{run_id}", response_model=RunEvent)
    def get_run(run_id: UUID) -> RunEvent:
        run = repo.get_by_run_id(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return run

    @app.get("/api/v1/threads/{thread_id}/runs", response_model=RunListResponse)
    def list_thread_runs(thread_id: str) -> RunListResponse:
        runs = repo.list_by_thread(thread_id)
        return RunListResponse(runs=runs, count=len(runs))

    @app.get("/api/v1/traces/{trace_id}/runs", response_model=RunListResponse)
    def list_trace_runs(trace_id: UUID) -> RunListResponse:
        runs = repo.list_by_trace(trace_id)
        return RunListResponse(runs=runs, count=len(runs))

    @app.get("/api/v1/report/users/{user_id}/threads", response_model=ThreadListResponse)
    def list_user_threads(user_id: str) -> ThreadListResponse:
        threads = repo.list_threads_for_user(user_id)
        return ThreadListResponse(user_id=user_id, threads=threads, count=len(threads))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse(url="/report")

    @app.get("/report", response_class=HTMLResponse)
    def report_home(
        thread_id: str | None = Query(default=None),
        user_id: str | None = Query(default=None),
        run_id: str | None = Query(default=None),
    ) -> str:
        return _render_split_home(
            repo,
            thread_id=thread_id,
            user_id=user_id,
            run_id=run_id,
        )

    @app.get("/report/users/{user_id}")
    def report_user_threads(user_id: str) -> RedirectResponse:
        return RedirectResponse(url=report_home_href(user_id=user_id))

    @app.get("/report/threads/{thread_id}")
    def report_thread_detail(
        thread_id: str,
        run_id: str | None = Query(default=None),
    ) -> RedirectResponse:
        runs = repo.list_by_thread(thread_id)
        resolved_user = None
        if runs:
            resolved_user = runs[0].metadata.get("user_id")
        return RedirectResponse(
            url=report_home_href(
                thread_id=thread_id,
                user_id=str(resolved_user) if resolved_user else None,
                run_id=run_id,
            )
        )

    @app.get("/report/runs/{run_id}", response_class=HTMLResponse)
    def report_run_detail(run_id: UUID) -> str:
        run = repo.get_by_run_id(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return run_detail_html(run)

    @app.get("/simulator", response_class=HTMLResponse)
    def simulator_page() -> str:
        return simulator_html()

    @app.post("/api/v1/simulator/run", response_model=SimulatorRunResponse)
    def simulator_run(
        body: SimulatorRunRequest,
        background_tasks: BackgroundTasks,
    ) -> SimulatorRunResponse:
        return start_simulator_run(background_tasks, body)

    @app.get("/api/v1/simulator/status", response_model=SimulatorStatusResponse)
    def simulator_status() -> SimulatorStatusResponse:
        return get_simulator_status()

    return app


def _render_split_home(
    repo: RunRepository,
    *,
    thread_id: str | None,
    user_id: str | None,
    run_id: str | None,
) -> str:
    users = repo.list_users_summary()
    threads_by_user = {
        user.user_id: repo.list_threads_for_user(user.user_id) for user in users
    }
    selected_runs: list[RunEvent] = []
    selected_user = user_id
    if thread_id:
        selected_runs = repo.list_by_thread(thread_id)
        if not selected_user and selected_runs:
            meta_user = selected_runs[0].metadata.get(META_USER_ID)
            if meta_user:
                selected_user = str(meta_user)
    return report_home_html(
        users,
        threads_by_user,
        selected_thread_id=thread_id,
        selected_user_id=selected_user,
        selected_runs=selected_runs,
        open_run_id=run_id,
    )


app = create_app()
