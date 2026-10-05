"""
tests/test_ranking.py

Phase 5.1 – verify hybrid relevance ranking scoring.
"""
import pytest

from backend.services.efficient_fetch.chunking import chunk_document
from backend.services.efficient_fetch.fetch_models import Chunk, SecurityElement
from backend.services.efficient_fetch.ranking import rank_chunks


def _make_chunk(index: int, text: str) -> Chunk:
    words = len(text.split())
    return Chunk(index=index, text=text, token_count=words)


class TestRankChunks:
    def test_empty_chunks_returns_empty(self):
        assert rank_chunks([], query_hint="login form") == []

    def test_returns_at_most_top_k(self):
        chunks = [_make_chunk(i, f"chunk number {i} with some text") for i in range(20)]
        result = rank_chunks(chunks, query_hint="chunk text", top_k=5)
        assert len(result) <= 5

    def test_relevant_chunk_ranked_above_unrelated(self):
        """A chunk about authentication should rank higher for a login query."""
        auth_chunk = _make_chunk(
            0,
            "login authentication username password form submit credentials",
        )
        unrelated_chunk = _make_chunk(
            1,
            "weather forecast temperature humidity wind speed rain probability",
        )
        result = rank_chunks([auth_chunk, unrelated_chunk], query_hint="login authentication form", top_k=2)
        assert result[0].chunk.index == 0, "Authentication chunk should be top-ranked"

    def test_scores_are_between_zero_and_one(self):
        chunks = [_make_chunk(i, f"text about topic {i}") for i in range(5)]
        result = rank_chunks(chunks, query_hint="topic", top_k=5)
        for ranked in result:
            assert 0.0 <= ranked.score <= 1.0

    def test_results_are_sorted_descending(self):
        chunks = [_make_chunk(i, f"irrelevant content {i}") for i in range(10)]
        # Make one highly relevant
        chunks[3] = _make_chunk(3, "file upload input type file form enctype multipart")
        result = rank_chunks(chunks, query_hint="file upload features", top_k=10)
        scores = [r.score for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_top_k_larger_than_chunks(self):
        """top_k > len(chunks) should return all chunks."""
        chunks = [_make_chunk(i, f"some content {i}") for i in range(3)]
        result = rank_chunks(chunks, query_hint="content", top_k=100)
        assert len(result) == 3

    # --- Phase 5.1 tests ---

    def test_hybrid_scoring_prioritizes_elements_with_signals(self):
        # Create a form element with strong security signals (password_field, login_form)
        auth_elem = SecurityElement(
            type="form",
            content={"action": "/login", "method": "POST"},
            security_signals=["password_field", "login_form", "csrf_token"],
            raw_snippet="<form action='/login'><input type='password'></form>"
        )
        auth_chunk = Chunk(
            index=0,
            text="some text representation of the form element",
            token_count=10,
            element=auth_elem
        )

        # Create a plain endpoint element
        unrelated_elem = SecurityElement(
            type="endpoint",
            content={"endpoint": "/about"},
            security_signals=[],
            raw_snippet="<a href='/about'>About Us</a>"
        )
        unrelated_chunk = Chunk(
            index=1,
            text="some text representation of the about link",
            token_count=10,
            element=unrelated_elem
        )

        chunks = [unrelated_chunk, auth_chunk]
        
        # Query hint targets authentication / login form
        result = rank_chunks(chunks, query_hint="authentication login form", top_k=2)
        
        # Verify the auth chunk ranks first
        assert result[0].chunk.index == 0
        assert result[0].score > result[1].score
