"""
tests/test_efficient_fetch.py

Phase 5.1 – verify the efficient_fetch() contract, JSON compression, and metrics.
"""
import json
import pytest

from backend.services.efficient_fetch import efficient_fetch, EfficientFetchResult

# 20 sections × ~80 unique words each = ~1 640 raw words.
# Each section paragraph is ~80 tokens → below _TARGET_MIN (500),
# so the chunker will merge them.  We deliberately use top_k=1 to
# guarantee efficient < naive regardless of merge grouping.
_LARGE_DOC = "\n\n".join(
    f"Section {i}: " + " ".join(f"word{i}_{j}" for j in range(80))
    for i in range(20)
)


class TestEfficientFetch:
    def test_returns_efficient_fetch_result(self):
        result = efficient_fetch("Hello world.\n\nThis is a test.", query_hint="test")
        assert isinstance(result, EfficientFetchResult)

    def test_contract_fields_present(self):
        result = efficient_fetch("Some content here.\n\nAnother paragraph.", query_hint="content")
        assert hasattr(result, "structured_content")
        assert hasattr(result, "token_count_naive")
        assert hasattr(result, "token_count_efficient")

    def test_context_reduction_occurs_on_large_document(self):
        """token_count_efficient must be less than token_count_naive for a large document."""
        # top_k=1 guarantees at most one chunk is returned which is
        # much smaller than the full 1 640-token document.
        result = efficient_fetch(_LARGE_DOC, query_hint="security features", top_k=1)
        assert result.token_count_naive > result.token_count_efficient

    def test_token_count_naive_reflects_full_document(self):
        doc = "word " * 500
        result = efficient_fetch(doc.strip(), query_hint="word", top_k=2)
        assert result.token_count_naive == 500

    def test_token_count_efficient_reflects_structured_content(self):
        result = efficient_fetch(_LARGE_DOC, query_hint="section", top_k=2)
        expected = len(result.structured_content.split())
        assert result.token_count_efficient == expected

    def test_structured_content_is_non_empty_for_non_empty_input(self):
        result = efficient_fetch("relevant security authentication login form", query_hint="login")
        assert result.structured_content.strip() != ""

    def test_empty_source_returns_zero_metrics(self):
        result = efficient_fetch("", query_hint="anything")
        assert result.token_count_naive == 0
        assert result.token_count_efficient == 0
        assert result.structured_content == ""

    def test_query_hint_influences_ranking(self):
        """Verify that the query hint is used: the ranking module selects
        the most relevant chunk.  We test this through rank_chunks directly
        to avoid hash-collision artefacts in the 64-dim bag-of-words embedding."""
        from backend.services.efficient_fetch.ranking import rank_chunks
        from backend.services.efficient_fetch.fetch_models import Chunk

        auth_chunk = Chunk(
            index=0,
            text="username password login form authentication credentials submit",
            token_count=8,
        )
        file_chunk = Chunk(
            index=1,
            text="file upload enctype multipart input type file documents attach",
            token_count=9,
        )
        chunks = [auth_chunk, file_chunk]

        auth_ranked = rank_chunks(chunks, query_hint="login authentication form", top_k=1)
        file_ranked = rank_chunks(chunks, query_hint="file upload enctype multipart", top_k=1)

        assert auth_ranked[0].chunk.index == 0, "Auth chunk should rank #1 for login query"
        assert file_ranked[0].chunk.index == 1, "File chunk should rank #1 for upload query"

    # --- Phase 5.1 tests ---

    def test_structured_json_output_on_html(self):
        html = """
        <html>
          <head>
            <!-- word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word -->
          </head>
          <body>
            <form action="/login" method="POST">
              <input type="text" name="user">
              <input type="password" name="pass">
            </form>
            <a href="/admin/settings">Admin Route</a>
          </body>
        </html>
        """
        result = efficient_fetch(html, query_hint="login forms", top_k=5)
        
        # Output should be valid JSON
        data = json.loads(result.structured_content)
        assert isinstance(data, dict)
        assert data["feature_context"] == "login forms"
        assert "forms" in data
        assert "hidden_fields" in data
        assert "detected_endpoints" in data

    def test_context_reduction_metrics_recorded(self):
        html = """
        <html>
          <head>
            <title>Dummy Page</title>
            <script>
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
              // noisy noisy noisy noisy noisy noisy noisy noisy noisy noisy
            </script>
            <style>body { color: blue; } h1 { font-size: 2em; }</style>
          </head>
          <body>
            <form action="/auth" method="POST">
              <input type="text" name="user">
              <input type="password" name="pass">
              <input type="hidden" name="token" value="abc">
            </form>
            <a href="/dashboard">Dashboard</a>
          </body>
        </html>
        """
        result = efficient_fetch(html, query_hint="login auth session", top_k=1)
        assert result.token_count_naive > result.token_count_efficient
        
        # Verify JSON properties of structured content
        data = json.loads(result.structured_content)
        assert len(data["forms"]) == 1
        assert data["forms"][0]["action"] == "/auth"
        assert data["forms"][0]["method"] == "POST"
        assert "password_field" in data["forms"][0]["signals"]
        assert "login_form" in data["forms"][0]["signals"]

