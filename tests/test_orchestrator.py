import asyncio

from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.recon_result import ReconResult
from backend.models.task import Task
from backend.models.worker_response import WorkerError, WorkerResponse
from backend.orchestrator.orchestrator import Orchestrator
from backend.orchestrator.task_dispatcher import TaskDispatcher
from backend.services.storage_service import get_features, get_findings, get_report, get_routes, get_tasks


class StubReconAgent:
    async def execute(self, task: Task) -> WorkerResponse:
        return WorkerResponse(
            status="success",
            worker="recon",
            task_id=task.task_id or "TASK-UNKNOWN",
            data={
                "url": task.target,
                "forms": [],
                "inputs": ["username", "password"],
                "buttons": ["Login"],
                "links": ["/register"],
                "scripts": [],
                "meta_tags": [],
            },
            new_findings=[],
            errors=[],
        )


class FailingReconAgent:
    async def execute(self, task: Task) -> WorkerResponse:
        return WorkerResponse(
            status="failure",
            worker="recon",
            task_id=task.task_id or "TASK-UNKNOWN",
            data={},
            new_findings=[],
            errors=[
                WorkerError(
                    error_type="DNS_RESOLUTION_FAILED",
                    message="Unable to resolve hostname",
                )
            ],
        )


class StubFeatureExtractionAgent:
    async def execute(self, task: Task) -> WorkerResponse:
        return WorkerResponse(
            status="success",
            worker="feature_extraction",
            task_id=task.task_id or "TASK-UNKNOWN",
            data=Feature(
                name="authentication",
                routes=[task.target],
                classification_confidence=0.96,
                analyzed=False,
            ).model_dump(),
            new_findings=[],
            errors=[],
        )


class StubAnalysisAgent:
    async def execute(self, task: Task) -> WorkerResponse:
        finding = Finding(
            type="missing_csrf",
            title="Potential Missing CSRF Protection",
            feature="authentication",
            severity="low",
            security_confidence=0.84,
            evidence=["POST login form detected", "No CSRF token observed"],
            description="The login form appears to submit without an observed CSRF token.",
            route_id=1,
        )
        return WorkerResponse(
            status="success",
            worker="analysis",
            task_id=task.task_id or "TASK-UNKNOWN",
            data={"analysis": finding.model_dump(), "persisted": True},
            new_findings=[finding.model_dump()],
            errors=[],
        )


class StubSemanticMemory:
    def __init__(self) -> None:
        self.initialized = False
        self.routes: list[tuple] = []
        self.features: list[Feature] = []
        self.findings: list[Finding] = []

    def initialize(self) -> None:
        self.initialized = True

    def upsert_route(self, route, recon_result=None) -> None:
        self.routes.append((route, recon_result))

    def upsert_feature(self, feature: Feature) -> None:
        self.features.append(feature)

    def upsert_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def search_routes(self, query: str, limit: int = 3):
        return []

    def search_features(self, query: str, limit: int = 3):
        return []

    def search_findings(self, query: str, limit: int = 3):
        return []


class TestOrchestrator:
    def test_mission_creation(self, tmp_path) -> None:
        semantic_memory = StubSemanticMemory()
        orchestrator = Orchestrator(
            dispatcher=TaskDispatcher(
                recon_agent=StubReconAgent(),
                feature_extraction_agent=StubFeatureExtractionAgent(),
                analysis_agent=StubAnalysisAgent(),
            ),
            db_path=str(tmp_path / "orchestrator.db"),
            semantic_memory=semantic_memory,
        )
        mission = orchestrator.create_mission("https://example.com")
        assert mission.mission_id == "MISSION-001"
        assert mission.target == "https://example.com"
        assert mission.status == "running"
        assert mission.coverage.recon_completed is False

    def test_state_updates_and_mission_completion(self, tmp_path) -> None:
        db_path = str(tmp_path / "orchestrator.db")
        semantic_memory = StubSemanticMemory()
        orchestrator = Orchestrator(
            dispatcher=TaskDispatcher(
                recon_agent=StubReconAgent(),
                feature_extraction_agent=StubFeatureExtractionAgent(),
                analysis_agent=StubAnalysisAgent(),
            ),
            db_path=db_path,
            semantic_memory=semantic_memory,
        )

        mission = asyncio.run(orchestrator.run("https://example.com"))

        assert mission.status == "completed"
        assert mission.coverage.recon_completed is True
        assert mission.features_extracted is True
        assert mission.analysis_completed is True
        assert orchestrator.last_response is not None
        assert orchestrator.last_response.status == "success"
        assert orchestrator.last_saved_route is not None
        assert orchestrator.last_saved_route.url == "https://example.com"
        assert orchestrator.last_saved_feature is not None
        assert orchestrator.last_saved_feature.name == "authentication"
        assert len(orchestrator.last_saved_findings) == 1
        assert orchestrator.last_saved_findings[0].finding_id == "FIND-001"
        assert semantic_memory.initialized is True
        assert len(semantic_memory.routes) == 1
        assert len(semantic_memory.features) == 1
        assert len(semantic_memory.findings) == 1
        assert isinstance(semantic_memory.routes[0][1], ReconResult)
        findings = get_findings(db_path=db_path)
        assert len(findings) == 1

    def test_task_generation_and_persistence(self, tmp_path) -> None:
        db_path = str(tmp_path / "orchestrator.db")
        semantic_memory = StubSemanticMemory()
        orchestrator = Orchestrator(
            dispatcher=TaskDispatcher(
                recon_agent=StubReconAgent(),
                feature_extraction_agent=StubFeatureExtractionAgent(),
                analysis_agent=StubAnalysisAgent(),
            ),
            db_path=db_path,
            semantic_memory=semantic_memory,
        )

        asyncio.run(orchestrator.run("https://example.com"))
        tasks = get_tasks(db_path=db_path)
        routes = get_routes(db_path=db_path)
        features = get_features(db_path=db_path)
        findings = get_findings(db_path=db_path)
        report = get_report(db_path=db_path)

        assert [task.action for task in tasks] == [
            "RUN_RECON",
            "EXTRACT_FEATURES",
            "RUN_EFFICIENT_FETCH",
            "RUN_ANALYSIS",
            "GENERATE_REPORT",
            "STOP",
        ]
        assert [task.status for task in tasks] == [
            "completed",
            "completed",
            "completed",
            "completed",
            "completed",
            "completed",
        ]
        assert tasks[0].task_id == "TASK-001"
        assert tasks[1].task_id == "TASK-002"
        assert tasks[2].task_id == "TASK-003"
        assert tasks[3].task_id == "TASK-004"
        assert tasks[4].task_id == "TASK-005"
        assert tasks[5].task_id == "TASK-006"
        assert len(routes) == 1
        assert routes[0].url == "https://example.com"
        assert len(features) == 1
        assert features[0].name == "authentication"
        assert len(findings) == 1
        assert findings[0].title == "Potential Missing CSRF Protection"
        assert report is not None
        assert report.report_id == "REPORT-001"

    def test_failure_response_marks_mission_failed_and_stops(self, tmp_path) -> None:
        db_path = str(tmp_path / "orchestrator.db")
        semantic_memory = StubSemanticMemory()
        orchestrator = Orchestrator(
            dispatcher=TaskDispatcher(
                recon_agent=FailingReconAgent(),
                feature_extraction_agent=StubFeatureExtractionAgent(),
                analysis_agent=StubAnalysisAgent(),
            ),
            db_path=db_path,
            semantic_memory=semantic_memory,
        )

        mission = asyncio.run(orchestrator.run("https://does-not-resolve.example"))
        tasks = get_tasks(db_path=db_path)
        routes = get_routes(db_path=db_path)

        assert mission.status == "failed"
        assert orchestrator.last_response is not None
        assert orchestrator.last_response.status == "failure"
        assert orchestrator.last_response.errors[0].error_type == "DNS_RESOLUTION_FAILED"
        assert [task.action for task in tasks] == ["RUN_RECON", "STOP"]
        assert [task.status for task in tasks] == ["failed", "completed"]
        assert routes == []
