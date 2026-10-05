"""
backend/models/feature.py

Pydantic model for a classified application feature.
Contract source: docs/contracts.md § 6 - Feature Object
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field

FeatureName = Literal[
    "authentication",
    "registration",
    "password_reset",
    "search",
    "file_upload",
    "api",
    "user_profile",
    "admin_panel",
    "dashboard",
    "settings",
    "unknown",
]


class Feature(BaseModel):
    feature_id: Optional[str] = None
    name: FeatureName
    routes: list[str] = Field(default_factory=list)
    classification_confidence: float = Field(ge=0.0, le=1.0)
    analyzed: bool = False
