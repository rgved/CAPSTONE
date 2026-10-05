"""
backend/models/worker_response.py

Worker response contract shared by all workers.
Contract source: docs/contracts.md Section 2 - Worker Response Contract
"""
from typing import Any, Literal

from pydantic import BaseModel, Field


class WorkerError(BaseModel):
    error_type: str
    message: str


class WorkerResponse(BaseModel):
    status: Literal["success", "failure"]
    worker: str
    task_id: str
    data: dict[str, Any] = Field(default_factory=dict)
    new_findings: list[Any] = Field(default_factory=list)
    errors: list[WorkerError] = Field(default_factory=list)
