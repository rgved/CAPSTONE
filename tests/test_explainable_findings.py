"""
tests/test_explainable_findings.py

Unit tests for Explainable Findings with Structured Evidence and Reasoning (Feature #11).
"""
import asyncio
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
from backend.agents.analysis.analysis_agent import AnalysisAgent
from backend.agents.report.report_agent import ReportAgent
from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.recon_result import ReconResult
from backend.models.route import Route
from backend.models.task import Task
from backend.memory.sqlite.database import init_db
from backend.services.storage_service import get_findings, save_finding


class StubAnalysisClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


def test_analysis_agent_extracts_reasoning() -> None:
    client = StubAnalysisClient(
        """
        {
          "finding_category": "missing_csrf",
          "title": "Missing Anti-CSRF Token on Authentication",
          "description": "The login form accepts state-changing POST requests without an anti-CSRF token.",
          "reasoning": "Unauthenticated POST submission on high-privilege login boundary lacks nonce or token validation, exposing users to cross-site credential forgery.",
          "severity": "medium",
          "confidence": 0.88,
          "evidence": [
            "POST method form identified at /login",
            "No hidden csrfmiddlewaretoken or similar input observed",
            "Session cookies lack SameSite=Strict attribute"
          ]
        }
        """
    )
    agent = AnalysisAgent(llm_client=client)
    task_context = {
        "feature": Feature(
            feature_id="AUTH-001",
            name="authentication",
            routes=["https://example.com/login"],
            classification_confidence=0.95,
            analyzed=False,
        ).model_dump(),
        "recon_result": ReconResult(
            url="https://example.com/login",
            forms=[],
            inputs=["username", "password"],
            buttons=["Submit"],
            links=[],
            scripts=[],
            meta_tags=[],
        ).model_dump(),
        "efficient_fetch_result": {"structured_content": "login form"},
        "semantic_context": {"similar_routes": [], "similar_features": [], "previous_findings": []},
        "route_id": 42,
    }
    task = Task(task_id="TASK-101", action="RUN_ANALYSIS", target="https://example.com/login", context=task_context)

    response = asyncio.run(agent.execute(task))

    assert response.status == "success"
    assert len(response.new_findings) == 1
    finding_data = response.new_findings[0]
    assert finding_data["type"] == "missing_csrf"
    assert "cross-site credential forgery" in finding_data["reasoning"]
    assert finding_data["security_confidence"] == 0.88
    assert len(finding_data["evidence"]) == 3


def test_explainable_finding_sqlite_persistence() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_explainable.db")
        init_db(db_path=db_path)

        finding = Finding(
            type="admin_surface",
            title="Exposed Administration Console",
            feature="admin_panel",
            severity="high",
            security_confidence=0.94,
            evidence=["/admin path reachable without active session header", "Admin login prompt returned 200 OK"],
            description="Administration surface is directly accessible over the public network.",
            reasoning="Unrestricted public routing to internal administrative functions presents an immediate attack surface for credential brute-forcing and privilege escalation.",
            route_id=10,
        )

        saved = save_finding(finding, db_path=db_path)
        assert saved.finding_id is not None
        assert saved.reasoning == finding.reasoning

        retrieved = get_findings(db_path=db_path)
        assert len(retrieved) == 1
        assert retrieved[0].reasoning == finding.reasoning
        assert retrieved[0].security_confidence == 0.94
        assert len(retrieved[0].evidence) == 2


def test_report_agent_propagates_reasoning() -> None:
    finding = Finding(
        finding_id="FIND-001",
        type="weak_authentication",
        title="Insecure Credential Transmission",
        feature="authentication",
        severity="medium",
        security_confidence=0.85,
        evidence=["Form action transmits credentials over cleartext HTTP"],
        description="Login form submits over plaintext HTTP.",
        reasoning="Transmitting sensitive authentication credentials without TLS encryption allows eavesdropping and credential theft on untrusted networks.",
    )
    feature = Feature(name="authentication", routes=["http://example.com/login"], classification_confidence=0.9, analyzed=True)
    route = Route(url="http://example.com/login", discovered_at=datetime.now(timezone.utc))

    agent = ReportAgent()
    report = agent.build_report(
        mission_id="MISSION-001",
        target_url="http://example.com/login",
        findings=[finding],
        features=[feature],
        routes=[route],
    )

    assert len(report.findings) == 1
    report_finding = report.findings[0]
    assert report_finding.reasoning == finding.reasoning
    assert report_finding.confidence == 0.85
