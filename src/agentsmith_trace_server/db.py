from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from uuid import UUID

from agentsmith_trace_server.models import RunEvent, RunStatus, ThreadSummary, UserSummary


class RunRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    parent_run_id TEXT,
                    trace_id TEXT NOT NULL,
                    run_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    inputs_json TEXT NOT NULL,
                    outputs_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_trace_id ON runs(trace_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_thread_id ON runs(json_extract(metadata_json, '$.thread_id'))"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_start_time ON runs(start_time)"
            )

    def upsert(self, event: RunEvent) -> RunEvent:
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT * FROM runs WHERE run_id = ?",
                (str(event.run_id),),
            ).fetchone()

            if existing:
                merged = self._merge_row(existing, event)
                conn.execute(
                    """
                    UPDATE runs SET
                        parent_run_id = ?,
                        trace_id = ?,
                        run_type = ?,
                        name = ?,
                        status = ?,
                        start_time = ?,
                        end_time = ?,
                        inputs_json = ?,
                        outputs_json = ?,
                        metadata_json = ?
                    WHERE run_id = ?
                    """,
                    merged,
                )
            else:
                conn.execute(
                    """
                    INSERT INTO runs (
                        run_id, parent_run_id, trace_id, run_type, name, status,
                        start_time, end_time, inputs_json, outputs_json, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._event_to_row(event),
                )
        return event

    def list_by_thread(self, thread_id: str) -> list[RunEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM runs
                WHERE json_extract(metadata_json, '$.thread_id') = ?
                ORDER BY start_time ASC
                """,
                (thread_id,),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def list_by_trace(self, trace_id: UUID) -> list[RunEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM runs
                WHERE trace_id = ?
                ORDER BY start_time ASC
                """,
                (str(trace_id),),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def get_most_recent_thread(self) -> tuple[str, str] | None:
        """Return (thread_id, user_id) for the thread with the latest run activity."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    json_extract(metadata_json, '$.thread_id') AS thread_id,
                    json_extract(metadata_json, '$.user_id') AS user_id
                FROM runs
                WHERE json_extract(metadata_json, '$.thread_id') IS NOT NULL
                GROUP BY thread_id
                ORDER BY MAX(start_time) DESC
                LIMIT 1
                """
            ).fetchone()
        if row is None or not row["thread_id"]:
            return None
        return str(row["thread_id"]), str(row["user_id"] or "_unknown")

    def list_threads_for_user(self, user_id: str) -> list[ThreadSummary]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    json_extract(metadata_json, '$.thread_id') AS thread_id,
                    COUNT(*) AS run_count,
                    MAX(start_time) AS last_activity
                FROM runs
                WHERE json_extract(metadata_json, '$.user_id') = ?
                  AND json_extract(metadata_json, '$.thread_id') IS NOT NULL
                GROUP BY thread_id
                ORDER BY last_activity DESC
                """,
                (user_id,),
            ).fetchall()
        return [
            ThreadSummary(
                thread_id=row["thread_id"],
                run_count=row["run_count"],
                last_activity=row["last_activity"],
            )
            for row in rows
        ]

    def get_by_run_id(self, run_id: UUID) -> RunEvent | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM runs WHERE run_id = ?",
                (str(run_id),),
            ).fetchone()
        if not row:
            return None
        return self._row_to_event(row)

    def list_users_summary(self) -> list[UserSummary]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    COALESCE(json_extract(metadata_json, '$.user_id'), '_unknown') AS user_id,
                    COUNT(DISTINCT json_extract(metadata_json, '$.thread_id')) AS thread_count,
                    COUNT(*) AS run_count,
                    MAX(start_time) AS last_activity
                FROM runs
                WHERE json_extract(metadata_json, '$.thread_id') IS NOT NULL
                GROUP BY user_id
                ORDER BY last_activity DESC
                """
            ).fetchall()
        return [
            UserSummary(
                user_id=row["user_id"],
                thread_count=row["thread_count"],
                run_count=row["run_count"],
                last_activity=row["last_activity"],
            )
            for row in rows
        ]

    def _merge_row(self, existing: sqlite3.Row, event: RunEvent) -> tuple:
        current = self._row_to_event(existing)
        if not event.inputs and current.inputs:
            event.inputs = current.inputs
        if not event.outputs and current.outputs:
            event.outputs = current.outputs
        if event.parent_run_id is None:
            event.parent_run_id = current.parent_run_id
        if event.end_time is None:
            event.end_time = current.end_time
        if event.status == RunStatus.PENDING and current.status != RunStatus.PENDING:
            event.status = current.status
        merged_meta = {**current.metadata, **event.metadata}
        event.metadata = merged_meta
        row = self._event_to_row(event)
        # UPDATE binds SET columns (skip run_id) then WHERE run_id
        return row[1:] + (row[0],)

    def _event_to_row(self, event: RunEvent) -> tuple:
        return (
            str(event.run_id),
            str(event.parent_run_id) if event.parent_run_id else None,
            str(event.trace_id),
            event.run_type.value,
            event.name,
            event.status.value,
            event.start_time.isoformat(),
            event.end_time.isoformat() if event.end_time else None,
            json.dumps(event.inputs, default=str),
            json.dumps(event.outputs, default=str),
            json.dumps(event.metadata, default=str),
        )

    def _row_to_event(self, row: sqlite3.Row) -> RunEvent:
        return RunEvent.model_validate(
            {
                "run_id": row["run_id"],
                "parent_run_id": row["parent_run_id"],
                "trace_id": row["trace_id"],
                "run_type": row["run_type"],
                "name": row["name"],
                "status": row["status"],
                "start_time": row["start_time"],
                "end_time": row["end_time"],
                "inputs": json.loads(row["inputs_json"]),
                "outputs": json.loads(row["outputs_json"]),
                "metadata": json.loads(row["metadata_json"]),
            }
        )


def default_db_path() -> Path:
    return Path(os.environ.get("AGENTSMITH_TRACE_DB", "agentsmith_trace.db"))
