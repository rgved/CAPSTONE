"""
backend/models/form.py

Pydantic model for a discovered HTML form.
Contract source: docs/contracts.md § 4 — Form Object

Fields
------
action  : The form's action attribute (URL target).
method  : HTTP method. Defaults to GET per HTML spec.
          UNKNOWN used when attribute value is unrecognised.
"""
from typing import Any, Literal

from pydantic import BaseModel, Field

# Allowed values per contracts.md §4
HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "UNKNOWN"]


class Form(BaseModel):
    action: str
    method: HttpMethod = "GET"
    enctype: str = "application/x-www-form-urlencoded"
    id: str = ""
    inputs: list[dict[str, Any]] = Field(default_factory=list)
