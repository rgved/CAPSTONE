"""
backend/models/task.py

Pydantic model for an orchestrator task.
Contract source: docs/contracts.md Section 1 - Task Contract
"""
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Task(BaseModel):
    task_id: Optional[str] = None
    action: str
    target: str
    context: dict[str, Any] = Field(default_factory=dict)
    priority: Literal["low", "medium", "high"] = "medium"
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    mission_id: Optional[str] = None

