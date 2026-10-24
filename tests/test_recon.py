"""
tests/test_recon.py

Unit tests for ReconAgent.parse_html().

All tests use static HTML strings — no Playwright, no network calls.
This keeps the test suite fast and deterministic.

Coverage (docs/phases/phase1.md — Unit Testing / HTML Parsing):
  - Links extracted correctly
  - Forms extracted correctly (action, method, default method, unknown method)
  - Inputs extracted correctly
  - Buttons extracted correctly
  - Scripts extracted correctly
  - Meta tags extracted correctly
  - Edge cases: empty href, unnamed inputs, anchor-only hrefs
"""
import pytest
import asyncio
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from backend.agents.recon.recon_agent import ReconAgent
from backend.models.recon_result import ReconResult
from backend.models.task import Task

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def agent() -> ReconAgent:
    return ReconAgent()


# ── Sample HTML ───────────────────────────────────────────────────────────────

FULL_HTML = """
<html>
<head>
  <meta name="generator" content="WordPress 6.4">
  <meta name="description" content="A sample site">
  <meta charset="utf-8">
  <script src="/static/app.js"></script>
  <script src="https://cdn.example.com/lib.js"></script>
  <script>/* inline — no src, should be ignored */</script>
</head>
<body>
  <nav>
    <a href="/home">Home</a>
    <a href="/about">About</a>
    <a href="#">Skip</a>
    <a href="">Empty</a>
  </nav>

  <form action="/login" method="POST">
    <input type="text"     name="username"  placeholder="Username">
    <input type="password" name="password"  placeholder="Password">
    <input type="hidden"   name="csrf_token" value="abc123">
    <input type="submit">
    <button type="submit">Login</button>
  </form>

  <form action="/search" method="GET">
    <input name="q" type="text">
    <button>Search</button>
  </form>

  <form action="/upload" method="PATCH">
    <input name="file" type="file">
    <button>Upload</button>
  </form>
</body>
</html>
"""


# ── Helper ────────────────────────────────────────────────────────────────────

def parse(agent: ReconAgent, html: str = FULL_HTML) -> ReconResult:
    return agent.parse_html("https://example.com", html)


# ── Link extraction ───────────────────────────────────────────────────────────

class TestLinkExtraction:
    def test_valid_links_extracted(self, agent: ReconAgent) -> None:
        result = parse(agent)
        assert "/home" in result.links
        assert "/about" in result.links

    def test_anchor_hash_excluded(self, agent: ReconAgent) -> None:
        result = parse(agent)
        assert "#" not in result.links

    def test_empty_href_excluded(self, agent: ReconAgent) -> None:
        result = parse(agent)
        assert "" not in result.links

    def test_no_links_when_none_present(self, agent: ReconAgent) -> None:
        result = parse(agent, "<html><body><p>No links here</p></body></html>")
        assert result.links == []


# ── Form extraction ───────────────────────────────────────────────────────────

class TestFormExtraction:
    def test_correct_number_of_forms(self, agent: ReconAgent) -> None:
        result = parse(agent)
        assert len(result.forms) == 3

    def test_login_form_action_and_method(self, agent: ReconAgent) -> None:
        result = parse(agent)
        login_form = result.forms[0]
        assert login_form.action == "/login"
        assert login_form.method == "POST"

    def test_search_form_get_method(self, agent: ReconAgent) -> None:
        result = parse(agent)
        search_form = result.forms[1]
        assert search_form.action == "/search"
        assert search_form.method == "GET"

    def test_unknown_method_mapped(self, agent: ReconAgent) -> None:
        # PATCH is not in the contract — must become UNKNOWN
        result = parse(agent)
        upload_form = result.forms[2]
        assert upload_form.method == "UNKNOWN"

    def test_form_with_no_method_defaults_to_get(self, agent: ReconAgent) -> None:
        html = '<html><body><form action="/test"><input name="x"></form></body></html>'
        result = parse(agent, html)
        assert result.forms[0].method == "GET"

    def test_form_with_empty_action_defaults_to_slash(self, agent: ReconAgent) -> None:
        html = '<html><body><form><input name="x"></form></body></html>'
        result = parse(agent, html)
        assert result.forms[0].action == "/"


# ── Input extraction ──────────────────────────────────────────────────────────

class TestInputExtraction:
    def test_named_inputs_extracted(self, agent: ReconAgent) -> None:
        result = parse(agent)
        assert "username" in result.inputs
        assert "password" in result.inputs
        assert "csrf_token" in result.inputs
        assert "q" in result.inputs
        assert "file" in result.inputs

    def test_unnamed_submit_button_excluded(self, agent: ReconAgent) -> None:
        # <input type="submit"> has no name attribute — should be excluded
        result = parse(agent)
        assert "" not in result.inputs

    def test_no_inputs_when_none_present(self, agent: ReconAgent) -> None:
        result = parse(agent, "<html><body><form></form></body></html>")
        assert result.inputs == []


# ── Button extraction ─────────────────────────────────────────────────────────

class TestButtonExtraction:
    def test_button_text_extracted(self, agent: ReconAgent) -> None:
        result = parse(agent)
        assert "Login" in result.buttons
        assert "Search" in result.buttons
        assert "Upload" in result.buttons

    def test_empty_button_excluded(self, agent: ReconAgent) -> None:
        html = '<html><body><button></button><button>  </button></body></html>'
        result = parse(agent, html)
        assert result.buttons == []


# ── Script extraction ─────────────────────────────────────────────────────────

class TestScriptExtraction:
    def test_external_scripts_extracted(self, agent: ReconAgent) -> None:
        result = parse(agent)
        assert "/static/app.js" in result.scripts
        assert "https://cdn.example.com/lib.js" in result.scripts

    def test_inline_scripts_excluded(self, agent: ReconAgent) -> None:
        # Inline <script> tags (no src attribute) must not appear
        result = parse(agent)
        assert len(result.scripts) == 2


# ── Meta tag extraction ───────────────────────────────────────────────────────

class TestMetaTagExtraction:
    def test_named_meta_tags_extracted(self, agent: ReconAgent) -> None:
        result = parse(agent)
        names = [tag["name"] for tag in result.meta_tags]
        assert "generator" in names
        assert "description" in names

    def test_meta_tag_content_correct(self, agent: ReconAgent) -> None:
        result = parse(agent)
        generator = next(t for t in result.meta_tags if t["name"] == "generator")
        assert generator["content"] == "WordPress 6.4"

    def test_charset_meta_excluded(self, agent: ReconAgent) -> None:
        # <meta charset="utf-8"> has no name attribute — must be excluded
        result = parse(agent)
        for tag in result.meta_tags:
            assert tag.get("name") != ""


class TimeoutReconAgent(ReconAgent):
    async def fetch_html(self, url: str) -> str:
        raise PlaywrightTimeoutError("Navigation timeout exceeded")


class DnsFailureReconAgent(ReconAgent):
    async def fetch_html(self, url: str) -> str:
        raise PlaywrightError("net::ERR_NAME_NOT_RESOLVED at https://missing.example")


class ConnectionRefusedReconAgent(ReconAgent):
    async def fetch_html(self, url: str) -> str:
        raise PlaywrightError("net::ERR_CONNECTION_REFUSED at http://127.0.0.1:9")


class DashboardFallbackReconAgent(ReconAgent):
    async def _fetch_html_with_playwright(self, url: str) -> str:
        raise NotImplementedError("subprocess transport not available")

    async def _fetch_html_with_http(self, url: str) -> str:
        return "<html><body><form action='/login' method='POST'><input name='username'><button>Login</button></form></body></html>"


class TestReconFailureHandling:
    def test_invalid_url_returns_failure_response(self) -> None:
        response = asyncio.run(
            ReconAgent().execute(
                Task(task_id="TASK-001", action="RUN_RECON", target="not-a-url", priority="high")
            )
        )

        assert response.status == "failure"
        assert response.worker == "recon"
        assert response.errors[0].error_type == "INVALID_URL"

    def test_nonexistent_domain_returns_dns_failure(self) -> None:
        response = asyncio.run(
            DnsFailureReconAgent().execute(
                Task(
                    task_id="TASK-002",
                    action="RUN_RECON",
                    target="https://does-not-resolve.example",
                    priority="high",
                )
            )
        )

        assert response.status == "failure"
        assert response.errors[0].error_type == "DNS_RESOLUTION_FAILED"
        assert response.errors[0].message == "Unable to resolve hostname"

    def test_timeout_returns_timeout_failure(self) -> None:
        response = asyncio.run(
            TimeoutReconAgent().execute(
                Task(task_id="TASK-003", action="RUN_RECON", target="https://example.com", priority="high")
            )
        )

        assert response.status == "failure"
        assert response.errors[0].error_type == "REQUEST_TIMEOUT"

    def test_connection_refused_returns_connection_failure(self) -> None:
        response = asyncio.run(
            ConnectionRefusedReconAgent().execute(
                Task(task_id="TASK-004", action="RUN_RECON", target="http://127.0.0.1:9", priority="high")
            )
        )

        assert response.status == "failure"
        assert response.errors[0].error_type == "CONNECTION_REFUSED"

    def test_dashboard_runtime_falls_back_to_http_fetch(self) -> None:
        response = asyncio.run(
            DashboardFallbackReconAgent().execute(
                Task(task_id="TASK-005", action="RUN_RECON", target="https://example.com/login", priority="high")
            )
        )

        assert response.status == "success"
        assert response.worker == "recon"
        assert response.data["url"] == "https://example.com/login"
        assert response.data["forms"][0]["action"] == "/login"
        assert response.data["buttons"] == ["Login"]

    def test_fetch_html_sync_handles_http_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import urllib.error
        from io import BytesIO

        def mock_urlopen(request, timeout=20, context=None):
            fp = BytesIO(b"<html><body><h1>404 Not Found</h1></body></html>")
            headers = {"Content-Type": "text/html"}
            raise urllib.error.HTTPError(
                url="https://example.com/notfound",
                code=404,
                msg="Not Found",
                hdrs=headers,
                fp=fp,
            )

        monkeypatch.setattr("backend.agents.recon.recon_agent.urlopen", mock_urlopen)
        agent = ReconAgent()
        html = agent._fetch_html_sync("https://example.com/notfound")
        assert "404 Not Found" in html
        assert agent._last_status == 404


class TestReactSPAExtraction:
    def test_react_non_form_buttons_and_inputs(self, agent: ReconAgent) -> None:
        react_spa_html = """
        <div id="root">
          <div class="login-card">
            <h2>Sign In to React App</h2>
            <input type="text" name="email" placeholder="Enter email" id="email-input" />
            <input type="password" name="password" placeholder="Enter password" id="pwd-input" />
            <button class="btn-primary" onClick="handleLogin()">Sign In</button>
            <button aria-label="OAuth Login"></button>
          </div>
        </div>
        """
        result = agent.parse_html("https://example.com/app", react_spa_html)

        # Standalone inputs extracted across the DOM without <form>
        assert "email" in result.inputs
        assert "password" in result.inputs
        assert len(result.forms) == 0

        # Standalone buttons extracted (including text and aria-label)
        assert "Sign In" in result.buttons
        assert "OAuth Login" in result.buttons

    def test_discovered_api_routes_merged_into_links(self, agent: ReconAgent) -> None:
        html = """
        <html>
          <body>
            <a href="/dashboard">Dashboard</a>
          </body>
        </html>
        """
        discovered_apis = {
            "https://example.com/api/v1/auth/login",
            "https://example.com/api/v1/users/profile",
            "https://example.com/actuator/health",
        }
        result = agent.parse_html(
            "https://example.com",
            html,
            discovered_api_routes=discovered_apis,
        )

        assert "/dashboard" in result.links
        assert "https://example.com/api/v1/auth/login" in result.links
        assert "https://example.com/api/v1/users/profile" in result.links
        assert "https://example.com/actuator/health" in result.links

    def test_extract_script_tags_with_integrity_and_cdn(self, agent: ReconAgent) -> None:
        html = """
        <html>
          <head>
            <script src="https://cdn.example.com/jquery-3.5.1.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.0.0/react.production.min.js" integrity="sha384-xyz" crossorigin="anonymous"></script>
            <script src="/static/bundle.js"></script>
          </head>
        </html>
        """
        result = agent.parse_html("https://example.com", html)
        assert len(result.script_tags) == 3
        # First script: external, no integrity
        s1 = next(s for s in result.script_tags if "jquery" in s["src"])
        assert s1["is_external"] is True
        assert s1["integrity"] is None

        # Second script: external, with integrity
        s2 = next(s for s in result.script_tags if "react" in s["src"])
        assert s2["is_external"] is True
        assert s2["integrity"] == "sha384-xyz"
        assert s2["crossorigin"] == "anonymous"

        # Third script: local bundle
        s3 = next(s for s in result.script_tags if "bundle.js" in s["src"])
        assert s3["is_external"] is False

    def test_extract_error_signatures_on_failure(self, agent: ReconAgent) -> None:
        html = """
        <html>
          <body>
            <h1>Internal Server Error</h1>
            <pre>Traceback (most recent call last):
              File "/app/server.py", line 42, in get
                ZeroDivisionError: division by zero
            </pre>
          </body>
        </html>
        """
        result = agent.parse_html("https://example.com/error", html, status_code=500)
        assert len(result.error_signatures) >= 2
        assert any("Traceback" in sig for sig in result.error_signatures)
        assert any("ZeroDivisionError" in sig for sig in result.error_signatures)

    def test_detect_reflected_parameters(self, agent: ReconAgent) -> None:
        html = """
        <html>
          <body>
            <h1>Search Results for: test_query</h1>
          </body>
        </html>
        """
        result = agent.parse_html("https://example.com/search?q=test_query", html)
        assert len(result.reflected_parameters) == 1
        assert result.reflected_parameters[0]["param"] == "q"
        assert result.reflected_parameters[0]["value"] == "test_query"
        assert result.reflected_parameters[0]["reflected"] is True

