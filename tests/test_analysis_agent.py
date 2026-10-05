import asyncio

from backend.agents.analysis.analysis_agent import AnalysisAgent
from backend.models.feature import Feature
from backend.models.recon_result import ReconResult
from backend.models.task import Task


class StubAnalysisClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


def _task_context() -> dict:
    return {
        "feature": Feature(
            feature_id="AUTH-001",
            name="authentication",
            routes=["https://example.com/login"],
            classification_confidence=0.96,
            analyzed=False,
        ).model_dump(),
        "recon_result": ReconResult(
            url="https://example.com/login",
            forms=[],
            inputs=["username", "password"],
            buttons=["Login"],
            links=["/register"],
            scripts=[],
            meta_tags=[],
        ).model_dump(),
        "efficient_fetch_result": {
            "structured_content": "POST login form no csrf token observed",
            "token_count_naive": 1200,
            "token_count_efficient": 120,
        },
        "semantic_context": {
            "similar_routes": [],
            "similar_features": [],
            "previous_findings": [],
        },
        "route_id": 7,
    }


class TestAnalysisAgent:
    def test_valid_finding_creation(self) -> None:
        client = StubAnalysisClient(
            """
            {
              "finding_category": "missing_csrf",
              "title": "Potential Missing CSRF Protection",
              "description": "The login flow appears to submit a POST form without any observed CSRF token.",
              "severity": "low",
              "confidence": 0.82,
              "evidence": ["POST login form detected", "No CSRF token observed"]
            }
            """
        )
        agent = AnalysisAgent(llm_client=client)
        task = Task(task_id="TASK-007", action="RUN_ANALYSIS", target="https://example.com/login", context=_task_context())

        response = asyncio.run(agent.execute(task))

        assert response.status == "success"
        assert response.worker == "analysis"
        assert response.data["persisted"] is True
        assert len(response.new_findings) == 1
        assert response.new_findings[0]["type"] == "missing_csrf"
        assert response.new_findings[0]["route_id"] == 7

    def test_confidence_threshold_suppresses_storage(self) -> None:
        client = StubAnalysisClient(
            """
            {
              "finding_category": "unknown",
              "title": "Informational Observation",
              "description": "The page exposes a login form but the evidence is not strong enough for a finding.",
              "severity": "informational",
              "confidence": 0.64,
              "evidence": ["Login form detected"]
            }
            """
        )
        agent = AnalysisAgent(llm_client=client)
        task = Task(task_id="TASK-008", action="RUN_ANALYSIS", target="https://example.com/login", context=_task_context())

        response = asyncio.run(agent.execute(task))

        assert response.status == "success"
        assert response.data["persisted"] is False
        assert response.new_findings == []

    def test_invalid_json_returns_failure(self) -> None:
        client = StubAnalysisClient("not-json")
        agent = AnalysisAgent(llm_client=client)
        task = Task(task_id="TASK-009", action="RUN_ANALYSIS", target="https://example.com/login", context=_task_context())

        response = asyncio.run(agent.execute(task))

        assert response.status == "failure"
        assert response.worker == "analysis"
        assert response.errors[0].error_type == "ANALYSIS_FAILED"

    def test_missing_context_returns_failure(self) -> None:
        client = StubAnalysisClient("{}")
        agent = AnalysisAgent(llm_client=client)
        task = Task(task_id="TASK-010", action="RUN_ANALYSIS", target="https://example.com/login", context={})

        response = asyncio.run(agent.execute(task))

        assert response.status == "failure"
        assert response.errors[0].error_type == "INVALID_TASK_CONTEXT"

    def test_deduplicated_evidence_package_with_structured_fetch(self) -> None:
        client = StubAnalysisClient(
            """
            {
              "finding_category": "missing_csrf",
              "title": "Missing CSRF Token",
              "description": "Form has no CSRF token",
              "severity": "medium",
              "confidence": 0.85,
              "evidence": ["POST form without CSRF"]
            }
            """
        )
        agent = AnalysisAgent(llm_client=client)
        ctx = _task_context()
        ctx["recon_result"]["forms"] = [{"action": "/raw_form", "method": "GET"}]
        ctx["recon_result"]["comments"] = ["<!-- secret comment -->"]
        ctx["recon_result"]["inline_scripts"] = ["console.log('test')"]
        ctx["efficient_fetch_result"] = {
            "structured_content": '{"forms": [{"action": "/login", "method": "POST", "signals": ["login_form"]}], "hidden_fields": [], "detected_endpoints": ["/login"]}',
            "token_count_naive": 5000,
            "token_count_efficient": 300,
        }

        task = Task(task_id="TASK-011", action="RUN_ANALYSIS", target="https://example.com/login", context=ctx)
        response = asyncio.run(agent.execute(task))

        assert response.status == "success"
        ev_pkg = response.data["evidence_package"]
        # Forms should come from efficient_fetch, not raw recon_result
        assert ev_pkg["forms"] == [{"action": "/login", "method": "POST", "signals": ["login_form"]}]
        assert ev_pkg["detected_endpoints"] == ["/login"]
        # Raw comments and inline_scripts should not be duplicated when efficient fetch is present
        assert "comments" not in ev_pkg
        assert "inline_scripts" not in ev_pkg
        # retrieved_context should not duplicate efficient_fetch
        for rc in ev_pkg["retrieved_context"]:
            assert rc.get("kind") != "efficient_fetch"

    def test_security_header_filtering(self) -> None:
        client = StubAnalysisClient(
            """
            {
              "finding_category": "missing_security_headers",
              "title": "Missing CSP",
              "description": "No CSP header",
              "severity": "low",
              "confidence": 0.80,
              "evidence": ["Server header present"]
            }
            """
        )
        agent = AnalysisAgent(llm_client=client)
        ctx = _task_context()
        # Large header set (> 5 keys) with noisy headers
        ctx["recon_result"]["headers"] = {
            "Date": "Wed, 21 Oct 2026 07:28:00 GMT",
            "Server": "nginx/1.18.0",
            "Content-Type": "text/html",
            "Content-Length": "348",
            "Connection": "keep-alive",
            "ETag": '"348-12345"',
            "X-Frame-Options": "DENY",
            "Keep-Alive": "timeout=5",
        }

        task = Task(task_id="TASK-012", action="RUN_ANALYSIS", target="https://example.com/login", context=ctx)
        response = asyncio.run(agent.execute(task))

        assert response.status == "success"
        ev_pkg = response.data["evidence_package"]
        headers = ev_pkg["headers"]
        # Security headers preserved
        assert "Server" in headers
        assert "X-Frame-Options" in headers
        # Noisy headers filtered out
        assert "Date" not in headers
        assert "ETag" not in headers
        assert "Keep-Alive" not in headers

