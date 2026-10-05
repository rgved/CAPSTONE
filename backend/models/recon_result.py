"""
backend/models/recon_result.py

Pydantic model for the primary output of the Recon Agent.
Contract source: docs/contracts.md § 5 — Recon Result Contract

Fields
------
url       : The URL that was scanned.
forms     : List of discovered HTML forms.
inputs    : List of discovered input field names.
buttons   : List of discovered button text labels.
links     : List of discovered href values.
scripts   : List of discovered external script src values.
meta_tags : List of relevant meta tag dicts {"name": ..., "content": ...}.
"""
from typing import Any

from pydantic import BaseModel, Field

from backend.models.form import Form


class ReconResult(BaseModel):
    url: str
    forms: list[Form] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    input_fields: list[dict[str, Any]] = Field(default_factory=list)
    buttons: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    scripts: list[str] = Field(default_factory=list)
    inline_scripts: list[str] = Field(default_factory=list)
    meta_tags: list[dict[str, Any]] = Field(default_factory=list)
    headers: dict[str, str] = Field(default_factory=dict)
    status_code: int = 200
    comments: list[str] = Field(default_factory=list)
