"""
backend/services/efficient_fetch/fetch_models.py

Pydantic models for the Efficient Fetch Service (Phase 5).
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class SecurityElement(BaseModel):
    """A structured representation of a security-relevant HTML component."""

    type: str = Field(..., description="Type of element (e.g., 'form', 'input', 'endpoint', 'upload').")
    content: dict = Field(..., description="Structured content values of the element.")
    security_signals: list[str] = Field(default_factory=list, description="Associated security signals.")
    raw_snippet: str = Field(..., description="Raw HTML snippet representing the element.")


class Chunk(BaseModel):
    """A single chunk of text produced by chunk_document()."""

    index: int = Field(..., description="Ordinal position within the source document.")
    text: str = Field(..., description="Raw text content of the chunk.")
    token_count: int = Field(..., description="Naive word-based token estimate.")
    element: SecurityElement | None = Field(default=None, description="Structured security element if present.")


class RankedChunk(BaseModel):
    """A Chunk paired with its relevance score against the query hint."""

    chunk: Chunk
    score: float = Field(..., description="Cosine similarity score (0–1, higher = more relevant).")


class EfficientFetchResult(BaseModel):
    """Output contract for efficient_fetch()."""

    structured_content: str = Field(
        ...,
        description="Concatenated top-K relevant chunk texts.",
    )
    token_count_naive: int = Field(
        ...,
        description="Naive word-based token count of the full source document.",
    )
    token_count_efficient: int = Field(
        ...,
        description="Naive word-based token count of the returned structured_content.",
    )

