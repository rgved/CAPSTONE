"""
backend/models/semantic_search_result.py

Pydantic model for semantic retrieval results returned by the Phase 4
retrieval layer.
"""
from typing import Union

from pydantic import BaseModel, Field

MetadataValue = Union[str, int, float, bool]


class SemanticSearchResult(BaseModel):
    document_id: str
    document: str
    metadata: dict[str, MetadataValue] = Field(default_factory=dict)
    distance: float | None = None
