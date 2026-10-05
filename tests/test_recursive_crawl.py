"""
tests/test_recursive_crawl.py

Unit tests for multi-route recursive crawling, URL normalization, and domain boundary filtering.
"""
import asyncio
import pytest

from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.recon_result import ReconResult
from backend.models.task import Task
from backend.models.worker_response import WorkerResponse
from backend.orchestrator.orchestrator import Orchestrator
from backend.orchestrator.task_dispatcher import TaskDispatcher
from backend.services.risk_scorer import is_same_domain, normalize_url
from backend.services.storage_service import get_routes, get_tasks


class MultiRouteStubReconAgent:
    def __init__(self) -> None:
        self.visited_urls: list[str] = []

    async def execute(self, task: Task) -> WorkerResponse:
        self.visited_urls.append(task.target)
        if task.target == "https://example.com":
            return WorkerResponse(
                status="success",
                worker="recon",
                task_id=task.task_id or "TASK-001",
                data={
                    "url": task.target,
                    "forms": [],
                    "inputs": ["search_query"],
                    "buttons": ["Search"],
                    "links": [
                        "/login",
                        "/admin",
                        "/static/style.css",
                        "https://external-domain.com/ad",
                    ],
                    "scripts": [],
                    "meta_tags": [],
                },
                new_findings=[],
                errors=[],
            )
        elif task.target == "https://example.com/login":
            return WorkerResponse(
                status="success",
                worker="recon",
                task_id=task.task_id or "TASK-002",
                data={
                    "url": task.target,
                    "forms": [{"action": "/login", "method": "POST"}],
                    "inputs": ["username", "password"],
                    "buttons": ["Sign In"],
                    "links": [],
                    "scripts": [],
                    "meta_tags": [],
                },
                new_findings=[],
                errors=[],
            )
        else:
            return WorkerResponse(
                status="success",
                worker="recon",
                task_id=task.task_id or "TASK-003",
                data={
                    "url": task.target,
                    "forms": [],
                    "inputs": [],
                    "buttons": [],
                    "links": [],
                    "scripts": [],
                    "meta_tags": [],
                },
                new_findings=[],
                errors=[],
            )


class StubFeatureExtractionAgent:
    async def execute(self, task: Task) -> WorkerResponse:
        return WorkerResponse(
            status="success",
            worker="feature_extraction",
            task_id=task.task_id or "TASK-004",
            data=Feature(
                name="authentication",
                routes=[task.target],
                classification_confidence=0.95,
                analyzed=False,
            ).model_dump(),
            new_findings=[],
            errors=[],
        )


class StubAnalysisAgent:
    async def execute(self, task: Task) -> WorkerResponse:
        finding = Finding(
            type="weak_authentication",
            title="Weak Password Authentication",
            feature="authentication",
            severity="medium",
            security_confidence=0.88,
            evidence=["POST /login detected"],
            description="Cleartext or weak password form.",
            route_id=1,
        )
        return WorkerResponse(
            status="success",
            worker="analysis",
            task_id=task.task_id or "TASK-005",
            data={"analysis": finding.model_dump(), "persisted": True},
            new_findings=[finding.model_dump()],
            errors=[],
        )


def test_url_normalization_and_domain_boundaries() -> None:
    seed = "https://app.target.com/home"
    assert normalize_url(seed, "/login") == "https://app.target.com/login"
    assert normalize_url(seed, "profile?id=12#header") == "https://app.target.com/profile?id=12"
    assert is_same_domain(seed, "https://app.target.com/admin") is True
    assert is_same_domain(seed, "https://other.com/admin") is False
    assert is_same_domain(seed, "javascript:void(0)") is False


def test_multi_route_crawling_orchestration(tmp_path) -> None:
    db_path = str(tmp_path / "multi_crawl.db")
    recon_agent = MultiRouteStubReconAgent()
    orchestrator = Orchestrator(
        dispatcher=TaskDispatcher(
            recon_agent=recon_agent,
            feature_extraction_agent=StubFeatureExtractionAgent(),
            analysis_agent=StubAnalysisAgent(),
        ),
        db_path=db_path,
        max_crawl_routes=2,
    )

    mission = asyncio.run(orchestrator.run("https://example.com"))

    assert mission.status == "completed"
    assert len(recon_agent.visited_urls) == 2
    assert recon_agent.visited_urls[0] == "https://example.com"
    # Second visited should be the high-risk prioritized /login or /admin endpoint from the target domain
    assert "https://example.com/" in recon_agent.visited_urls[1]

    routes = get_routes(db_path=db_path)
    assert len(routes) == 2


class FailingSubRouteReconAgent:
    def __init__(self) -> None:
        self.visited_urls: list[str] = []

    async def execute(self, task: Task) -> WorkerResponse:
        self.visited_urls.append(task.target)
        if task.target == "https://example.com":
            return WorkerResponse(
                status="success",
                worker="recon",
                task_id=task.task_id or "TASK-001",
                data={
                    "url": task.target,
                    "forms": [],
                    "inputs": ["search"],
                    "buttons": ["Go"],
                    "links": ["/broken-subpage"],
                    "scripts": [],
                    "meta_tags": [],
                },
                new_findings=[],
                errors=[],
            )
        else:
            return WorkerResponse(
                status="failure",
                worker="recon",
                task_id=task.task_id or "TASK-002",
                data={},
                new_findings=[],
                errors=[{"error_type": "RECON_FAILURE", "message": "HTTP Error 404: Not Found"}],
            )


def test_subroute_failure_does_not_abort_mission(tmp_path) -> None:
    db_path = str(tmp_path / "subroute_fail.db")
    recon_agent = FailingSubRouteReconAgent()
    orchestrator = Orchestrator(
        dispatcher=TaskDispatcher(
            recon_agent=recon_agent,
            feature_extraction_agent=StubFeatureExtractionAgent(),
            analysis_agent=StubAnalysisAgent(),
        ),
        db_path=db_path,
        max_crawl_routes=2,
    )

    mission = asyncio.run(orchestrator.run("https://example.com"))

    # Mission must complete successfully because root target was scanned
    assert mission.status == "completed"
    assert len(recon_agent.visited_urls) == 2
    assert recon_agent.visited_urls[0] == "https://example.com"
    assert recon_agent.visited_urls[1] == "https://example.com/broken-subpage"

