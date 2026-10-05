"""
tests/test_chunking.py

Phase 5.1 – verify HTML parsing, boilerplate stripping, and signal detection.
"""
import pytest

from backend.services.efficient_fetch.chunking import chunk_document, _naive_token_count


def _make_paragraph(words: int) -> str:
    return " ".join(f"word{i}" for i in range(words))


class TestChunkDocument:
    def test_empty_string_returns_no_chunks(self):
        assert chunk_document("") == []

    def test_whitespace_only_returns_no_chunks(self):
        assert chunk_document("   \n\n  ") == []

    def test_small_document_produces_at_least_one_chunk(self):
        chunks = chunk_document("Hello world.\n\nThis is a test.")
        assert len(chunks) >= 1

    def test_chunk_indices_are_sequential(self):
        doc = "\n\n".join(f"Paragraph {i}." for i in range(5))
        chunks = chunk_document(doc)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_chunk_token_count_matches_text(self):
        doc = "\n\n".join(_make_paragraph(50) for _ in range(4))
        chunks = chunk_document(doc)
        for chunk in chunks:
            assert chunk.token_count == _naive_token_count(chunk.text)

    def test_no_chunk_exceeds_max_target(self):
        """Each produced chunk must not exceed 1 000 tokens (the _TARGET_MAX)."""
        # Build a document with many short paragraphs.
        doc = "\n\n".join(_make_paragraph(30) for _ in range(40))
        chunks = chunk_document(doc)
        for chunk in chunks:
            assert chunk.token_count <= 1000, (
                f"Chunk {chunk.index} has {chunk.token_count} tokens"
            )

    def test_very_long_single_paragraph_is_split(self):
        """A paragraph of 2 000 tokens must be split into multiple chunks."""
        long_para = _make_paragraph(2000)
        chunks = chunk_document(long_para)
        assert len(chunks) >= 2

    def test_all_content_preserved(self):
        """The union of chunk texts should contain all original words."""
        words = [f"unique_{i}" for i in range(100)]
        doc = " ".join(words)
        chunks = chunk_document(doc)
        combined = " ".join(c.text for c in chunks)
        for word in words:
            assert word in combined

    # --- Phase 5.1 HTML tests ---

    def test_boilerplate_removal(self):
        html = """
        <html>
          <head>
            <title>Test Page</title>
            <script>alert("hello");</script>
            <style>body { color: red; }</style>
            <link rel="stylesheet" href="style.css">
            <link rel="dns-prefetch" href="//example.com">
          </head>
          <body>
            <form action="/login"><input type="text" name="username"></form>
          </body>
        </html>
        """
        chunks = chunk_document(html)
        # Verify boilerplate elements decomposed - the script/style/link shouldn't be present
        for c in chunks:
            assert "style.css" not in c.text
            assert "dns-prefetch" not in c.text
            assert "alert" not in c.text
            assert "username" in str(c.element.content)

    def test_security_structure_extraction(self):
        html = """
        <form action="/session" method="POST">
          <input type="text" name="login">
          <input type="password" name="password">
          <button type="submit">Log In</button>
        </form>
        <a href="/admin/dashboard">Admin Console</a>
        """
        chunks = chunk_document(html)
        types = [c.element.type for c in chunks if c.element]
        assert "form" in types
        assert "endpoint" in types

        # Find form elements
        form_el = [c.element for c in chunks if c.element and c.element.type == "form"][0]
        assert form_el.content["action"] == "/session"
        assert form_el.content["method"] == "POST"
        assert len(form_el.content["inputs"]) == 2
        assert form_el.content["inputs"][0]["name"] == "login"
        assert form_el.content["inputs"][1]["type"] == "password"

    def test_security_signal_detection(self):
        html = """
        <form action="/login" method="POST">
          <input type="password" name="pwd">
          <input type="hidden" name="authenticity_token" value="secret">
        </form>
        <form action="/upload" method="POST" enctype="multipart/form-data">
          <input type="file" name="file">
        </form>
        <a href="/admin/settings">Settings</a>
        """
        chunks = chunk_document(html)
        
        # Verify signal types on elements
        signals_map = {c.element.type: c.element.security_signals for c in chunks if c.element}
        
        # Admin endpoint
        admin_endpoint_signals = [c.element.security_signals for c in chunks if c.element and c.element.type == "endpoint"][0]
        assert "admin_route" in admin_endpoint_signals

        # Forms
        form_elements = [c.element for c in chunks if c.element and c.element.type == "form"]
        form1_signals = form_elements[0].security_signals
        form2_signals = form_elements[1].security_signals

        assert "password_field" in form1_signals
        assert "login_form" in form1_signals
        assert "csrf_token" in form1_signals
        
        assert "multipart_form" in form2_signals
        assert "file_input" in form2_signals
        assert "upload_endpoint" in form2_signals
