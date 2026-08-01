from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RunType(str, Enum):
    LLM = "llm"
    CHAIN = "chain"
    TOOL = "tool"


class RunStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class RunEvent(BaseModel):
    run_id: UUID
    parent_run_id: UUID | None = None
    trace_id: UUID
    run_type: RunType
    name: str
    status: RunStatus = RunStatus.PENDING
    start_time: datetime
    end_time: datetime | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunEventResponse(BaseModel):
    run_id: UUID
    stored: bool = True


class RunListResponse(BaseModel):
    runs: list[RunEvent]
    count: int


class UserSummary(BaseModel):
    user_id: str
    thread_count: int
    run_count: int
    last_activity: str | None = None


class ThreadSummary(BaseModel):
    thread_id: str
    run_count: int
    last_activity: str | None = None


class ThreadListResponse(BaseModel):
    user_id: str
    threads: list[ThreadSummary]
    count: int
