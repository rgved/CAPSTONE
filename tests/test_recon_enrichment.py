"""
tests/test_recon_enrichment.py

Unit tests for enriched recon extraction:
- Input attributes (type, value_present, placeholder, id)
- Form enctype (multipart/form-data)
- Comments and inline scripts extraction
- HTTP response headers & status code
"""
import pytest
from backend.agents.recon.recon_agent import ReconAgent
from backend.models.recon_result import ReconResult


ENRICHED_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Security Test App</title>
  <!-- TODO: remove staging API key: sk_test_51Mz8937 -->
  <script>
    window.APP_CONFIG = { apiEndpoint: "/api/v1/internal", debug: false };
  </script>
</head>
<body>
  <!-- Navigation section -->
  <a href="/dashboard">Dashboard</a>
  <a href="https://external-domain.com/ad">External Ad</a>

  <form id="upload-form" action="/api/v1/upload" method="POST" enctype="multipart/form-data">
    <input type="file" name="attachment" id="file-input" required>
    <input type="hidden" name="csrf_token" value="sec_nonce_999">
    <button type="submit">Upload</button>
  </form>

  <form id="login-form" action="/login" method="POST">
    <input type="text" name="username" placeholder="Enter username" autocomplete="username">
    <input type="password" name="password" placeholder="Enter password" autocomplete="current-password">
    <button type="submit">Log In</button>
  </form>
</body>
</html>
"""


def test_input_attributes_and_fields_extraction() -> None:
    agent = ReconAgent()
    result = agent.parse_html("https://example.com", ENRICHED_HTML)

    # Legacy field backwards-compatibility
    assert "attachment" in result.inputs
    assert "csrf_token" in result.inputs
    assert "username" in result.inputs
    assert "password" in result.inputs

    # Enriched input_fields
    fields_by_name = {f["name"]: f for f in result.input_fields if f["name"]}
    assert fields_by_name["attachment"]["type"] == "file"
    assert fields_by_name["csrf_token"]["type"] == "hidden"
    assert fields_by_name["csrf_token"]["value_present"] is True
    assert fields_by_name["username"]["type"] == "text"
    assert fields_by_name["username"]["placeholder"] == "Enter username"
    assert fields_by_name["password"]["type"] == "password"


def test_form_enctype_and_form_level_inputs() -> None:
    agent = ReconAgent()
    result = agent.parse_html("https://example.com", ENRICHED_HTML)

    assert len(result.forms) == 2
    upload_form = result.forms[0]
    assert upload_form.action == "/api/v1/upload"
    assert upload_form.method == "POST"
    assert upload_form.enctype == "multipart/form-data"
    assert upload_form.id == "upload-form"
    assert len(upload_form.inputs) == 2
    assert upload_form.inputs[0]["name"] == "attachment"
    assert upload_form.inputs[0]["type"] == "file"


def test_comments_and_inline_scripts_extraction() -> None:
    agent = ReconAgent()
    result = agent.parse_html("https://example.com", ENRICHED_HTML)

    assert any("sk_test_51Mz8937" in c for c in result.comments)
    assert any("APP_CONFIG" in s for s in result.inline_scripts)


def test_headers_and_status_code_passed_to_recon_result() -> None:
    agent = ReconAgent()
    custom_headers = {
        "Content-Type": "text/html",
        "Server": "gunicorn",
    }
    result = agent.parse_html("https://example.com", ENRICHED_HTML, headers=custom_headers, status_code=200)

    assert result.headers == custom_headers
    assert result.status_code == 200
