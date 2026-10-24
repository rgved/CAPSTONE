import asyncio
from datetime import datetime, timezone

from backend.agents.report.report_agent import ReportAgent
from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.route import Route
from backend.models.task import Task


class TestReportAgent:
    def test_report_generation(self) -> None:
        agent = ReportAgent()
        task = Task(
            task_id="TASK-010",
            action="GENERATE_REPORT",
            target="https://example.com",
            context={
                "mission_id": "MISSION-001",
                "target_url": "https://example.com",
                "findings": [
                    Finding(
                        finding_id="FIND-001",
                        type="missing_csrf",
                        title="Login Form Missing CSRF Protection",
                        feature="authentication",
                        severity="medium",
                        security_confidence=0.86,
                        evidence=["POST form detected", "No CSRF token observed"],
                        description="The login form submits without an observed CSRF token.",
                    ).model_dump()
                ],
                "features": [Feature(name="authentication", routes=["https://example.com/login"], classification_confidence=0.96, analyzed=False).model_dump()],
                "routes": [Route(route_id=1, url="https://example.com/login", discovered_at=datetime.now(timezone.utc)).model_dump()],
            },
        )

        response = asyncio.run(agent.execute(task))

        assert response.status == "success"
        assert response.worker == "report"
        assert response.data["report_id"] == "REPORT-001"
        assert response.new_findings == []

    def test_executive_summary_generation(self) -> None:
        agent = ReportAgent()
        report = agent.build_report(
            mission_id="MISSION-001",
            target_url="https://example.com",
            findings=[],
            features=[Feature(name="authentication", routes=["https://example.com/login"], classification_confidence=0.96, analyzed=False)],
            routes=[Route(route_id=1, url="https://example.com/login", discovered_at=datetime.now(timezone.utc))],
        )

        assert "1 feature was" in report.executive_summary
        assert "0 findings were generated" in report.executive_summary

    def test_statistics_generation(self) -> None:
        agent = ReportAgent()
        report = agent.build_report(
            mission_id="MISSION-001",
            target_url="https://example.com",
            findings=[
                Finding(
                    finding_id="FIND-001",
                    type="missing_csrf",
                    title="Login Form Missing CSRF Protection",
                    feature="authentication",
                    severity="medium",
                    security_confidence=0.86,
                    evidence=["POST form detected"],
                    description="The login form submits without an observed CSRF token.",
                )
            ],
            features=[],
            routes=[],
        )

        assert report.statistics["routes_discovered"] == 0
        assert report.statistics["features_identified"] == 0
        assert report.statistics["findings_generated"] == 1
        assert report.statistics["severity_breakdown"]["Medium"] == 1

    def test_statistics_with_recon_discovery(self) -> None:
        agent = ReportAgent()
        sample_recon = {
            "forms": [{"action": "/login", "method": "POST"}],
            "inputs": ["email", "password"],
            "buttons": ["Sign In"],
            "scripts": ["/app.js"],
            "links": ["/home", "/about", "/login"],
            "meta_tags": [{"name": "description", "content": "Sample"}, {"name": "viewport", "content": "width=device-width"}],
            "comments": ["<!-- todo -->"],
        }
        report = agent.build_report(
            mission_id="MISSION-001",
            target_url="https://example.com",
            findings=[],
            features=[],
            routes=[],
            recon_result=sample_recon,
        )

        assert report.statistics["forms_count"] == 1
        assert report.statistics["inputs_count"] == 2
        assert report.statistics["buttons_count"] == 1
        assert report.statistics["scripts_count"] == 1
        assert report.statistics["links_count"] == 3
        assert report.statistics["meta_tags_count"] == 2
        assert report.statistics["comments_count"] == 1

    def test_report_findings_sorted_descending_by_severity(self) -> None:
        agent = ReportAgent()
        f_low = Finding(
            finding_id="FIND-001",
            type="missing_security_headers",
            title="Low Severity Header",
            feature="general",
            severity="low",
            security_confidence=0.8,
            evidence=[],
            description="Missing headers",
        )
        f_high = Finding(
            finding_id="FIND-002",
            type="missing_csrf",
            title="High Severity CSRF",
            feature="authentication",
            severity="high",
            security_confidence=0.9,
            evidence=[],
            description="CSRF missing",
        )
        f_med = Finding(
            finding_id="FIND-003",
            type="weak_authentication",
            title="Medium Severity Auth",
            feature="authentication",
            severity="medium",
            security_confidence=0.85,
            evidence=[],
            description="Weak auth",
        )
        report = agent.build_report(
            mission_id="MISSION-001",
            target_url="https://example.com",
            findings=[f_low, f_high, f_med],
            features=[],
            routes=[],
        )

        severities = [rf.severity.lower() for rf in report.findings]
        assert severities == ["high", "medium", "low"]

