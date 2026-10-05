"""
backend/services/efficient_fetch/ranking.py

Hybrid Relevance Ranking for the Efficient Fetch Service (Phase 5.1).

Combines:
1. Keyword Score (45%) - Jaccard overlap of query hint terms with security fields/signals.
2. Semantic Similarity (30%) - Cosine similarity using the vector space model.
3. Structural Bonus (25%) - Structural matching based on security signals.

Returns the top-K ranked chunks, preserving 0.0 to 1.0 score limits.
"""
from __future__ import annotations

import math
import re

from backend.services.efficient_fetch.fetch_models import Chunk, RankedChunk

_EMBEDDING_DIMENSION = 64
_TOKEN_PATTERN = re.compile(r"[a-z0-9_./:-]+")


def _embed(text: str) -> list[float]:
    """Deterministic bag-of-tokens embedding (identical to SemanticMemoryStore)."""
    vector = [0.0] * _EMBEDDING_DIMENSION
    tokens = _TOKEN_PATTERN.findall(text.lower())
    if not tokens:
        return vector

    for token in tokens:
        slot = hash(token) % _EMBEDDING_DIMENSION
        vector[slot] += 1.0

    magnitude = math.sqrt(sum(v * v for v in vector))
    if magnitude == 0.0:
        return vector
    return [v / magnitude for v in vector]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two unit-norm vectors."""
    return sum(x * y for x, y in zip(a, b))


def _get_keyword_score(chunk: Chunk, query_hint: str) -> float:
    """Calculates Jaccard overlap between query hint terms and element content."""
    query_terms = set(re.findall(r"[a-z0-9_]+", query_hint.lower()))
    if not query_terms:
        return 0.0

    element_text = chunk.text.lower()
    if chunk.element:
        # Include signals, type, and content representation
        element_text += " " + " ".join(chunk.element.security_signals)
        element_text += " " + chunk.element.type
        element_text += " " + str(chunk.element.content).lower()

    element_terms = set(re.findall(r"[a-z0-9_]+", element_text))
    matches = query_terms.intersection(element_terms)
    return len(matches) / len(query_terms)


def _get_structural_bonus(chunk: Chunk, query_hint: str) -> float:
    """Applies context-specific structural boosts based on elements and signals."""
    if not chunk.element:
        return 0.0

    q = query_hint.lower()
    elem = chunk.element
    signals = set(elem.security_signals)

    # Authentication Context
    if any(kw in q for kw in ["login", "auth", "signin", "session", "password"]):
        if elem.type == "form" or "login_form" in signals or "password_field" in signals:
            return 1.0
        if "csrf_token" in signals or "session_endpoint" in signals:
            return 0.8

    # File Upload Context
    if any(kw in q for kw in ["upload", "file", "multipart"]):
        if "file_input" in signals or "upload_endpoint" in signals or "multipart_form" in signals:
            return 1.0

    # Administrative Interfaces Context
    if any(kw in q for kw in ["admin", "manage"]):
        if "admin_route" in signals:
            return 1.0

    # Default structural boost for form controls over other elements
    if elem.type in ("form", "input"):
        return 0.2

    return 0.0


def rank_chunks(chunks: list[Chunk], query_hint: str, top_k: int = 5) -> list[RankedChunk]:
    """
    Score each chunk using hybrid scoring (45% keyword, 30% semantic, 25% structural).
    """
    if not chunks:
        return []

    query_vec = _embed(query_hint)
    scored: list[RankedChunk] = []

    for chunk in chunks:
        # 1. Semantic Score
        semantic_score = _cosine_similarity(query_vec, _embed(chunk.text))

        # 2. Keyword Score
        keyword_score = _get_keyword_score(chunk, query_hint)

        # 3. Structural Bonus
        structural_bonus = _get_structural_bonus(chunk, query_hint)

        # Combined weighted score (guaranteed to fall between 0.0 and 1.0)
        final_score = 0.45 * keyword_score + 0.30 * semantic_score + 0.25 * structural_bonus

        # Normalize/clamp to double-check boundary conditions
        final_score = max(0.0, min(1.0, final_score))

        scored.append(RankedChunk(chunk=chunk, score=final_score))

    scored.sort(key=lambda rc: rc.score, reverse=True)
    return scored[:top_k]
