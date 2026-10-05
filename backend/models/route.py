"""
backend/models/route.py

Pydantic model for a discovered route.
Contract source: docs/contracts.md § 3 — Route Object

Fields
------
route_id    : Assigned by SQLite AUTOINCREMENT on save. None before persisting.
url         : The full URL of the discovered route.
discovered_at : UTC timestamp of discovery.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Route(BaseModel):
    route_id: Optional[int] = None
    url: str
    discovered_at: datetime
