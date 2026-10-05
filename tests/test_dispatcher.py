import asyncio

from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.task import Task
from backend.models.worker_response import WorkerResponse
from backend.orchestrator.task_dispatcher import TaskDispatcher


class StubReconAgent:
    async def execute(self, task: Task) -> WorkerResponse:
        return WorkerResponse(
            status="success",
            worker="recon",
            task_id=task.task_id or "TASK-UNKNOWN",
            data={
                "url": task.target,
                "forms": [],
                "inputs": ["username"],
                "buttons": ["Login"],
                "links": ["/register"],
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


class StubEfficientFetchWorker:
    async def execute(self, task: Task) -> WorkerResponse:
        return WorkerResponse(
            status="success",
            worker="efficient_fetch_worker",
            task_id=task.task_id or "TASK-UNKNOWN",
            data={
                "structured_content": "login form authentication",
                "token_count_naive": 1000,
                "token_count_efficient": 50,
            },
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
            security_confidence=0.82,
            evidence=["POST form detected", "No CSRF token observed"],
            description="The login form lacks an observed CSRF token.",
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


def _make_dispatcher() -> TaskDispatcher:
    """Helper: dispatcher wired with all stubs — no real agents needed."""
    return TaskDispatcher(
        recon_agent=StubReconAgent(),
        feature_extraction_agent=StubFeatureExtractionAgent(),
        efficient_fetch_worker=StubEfficientFetchWorker(),
        analysis_agent=StubAnalysisAgent(),
    )


class TestTaskDispatcher:
    def test_run_recon_dispatches_to_recon_agent(self) -> None:
        dispatcher = _make_dispatcher()
        task = Task(task_id="TASK-001", action="RUN_RECON", target="https://example.com", priority="high")

        response = asyncio.run(dispatcher.dispatch(task))

        assert response.status == "success"
        assert response.worker == "recon"
        assert response.task_id == "TASK-001"
        assert response.data["url"] == "https://example.com"
        assert response.data["inputs"] == ["username"]

    def test_extract_features_dispatches_to_feature_agent(self) -> None:
        dispatcher = _make_dispatcher()
        task = Task(
            task_id="TASK-002",
            action="EXTRACT_FEATURES",
            target="https://example.com/login",
            context={"recon_result": {"url": "https://example.com/login"}},
            priority="high",
        )

        response = asyncio.run(dispatcher.dispatch(task))

        assert response.status == "success"
        assert response.worker == "feature_extraction"
        assert response.data["name"] == "authentication"
        assert response.data["routes"] == ["https://example.com/login"]

    def test_invalid_action_returns_failure_response(self) -> None:
        dispatcher = _make_dispatcher()
        task = Task(task_id="TASK-003", action="INVALID", target="https://example.com")

        response = asyncio.run(dispatcher.dispatch(task))

        assert response.status == "failure"
        assert response.worker == "dispatcher"
        assert response.errors[0].error_type == "UNSUPPORTED_ACTION"
        assert response.errors[0].message == "Unsupported action: INVALID"

    # ------------------------------------------------------------------ #
    # Phase 5 tests                                                        #
    # ------------------------------------------------------------------ #

    def test_run_efficient_fetch_dispatch(self) -> None:
        """RUN_EFFICIENT_FETCH must be routed to EfficientFetchWorker, not the
        unsupported-action fallback."""
        dispatcher = _make_dispatcher()
        task = Task(
            task_id="TASK-004",
            action="RUN_EFFICIENT_FETCH",
            target="https://example.com",
            context={
                "source_text": "login form authentication username password",
                "query_hint": "authentication forms",
            },
            priority="high",
        )

        response = asyncio.run(dispatcher.dispatch(task))

        # Must succeed — not an UNSUPPORTED_ACTION failure.
        assert response.status == "success", (
            f"Expected success but got failure: {response.errors}"
        )
        assert response.worker == "efficient_fetch_worker"
        assert response.task_id == "TASK-004"

    def test_efficient_fetch_worker_response(self) -> None:
        """WorkerResponse from RUN_EFFICIENT_FETCH must conform to contracts.md:
        status, worker, task_id, data, new_findings, errors all present."""
        dispatcher = _make_dispatcher()
        task = Task(
            task_id="TASK-005",
            action="RUN_EFFICIENT_FETCH",
            target="https://example.com",
            context={
                "source_text": "admin panel dashboard file upload input search",
                "query_hint": "file upload features",
            },
            priority="high",
        )

        response = asyncio.run(dispatcher.dispatch(task))

        # --- contracts.md WorkerResponse fields ---
        assert response.status in ("success", "failure")
        assert isinstance(response.worker, str) and response.worker != ""
        assert response.task_id == "TASK-005"
        assert isinstance(response.data, dict)
        assert isinstance(response.new_findings, list)
        assert isinstance(response.errors, list)

        # --- Phase 5 data contract ---
        assert response.status == "success"
        assert "structured_content" in response.data
        assert "token_count_naive" in response.data
        assert "token_count_efficient" in response.data
        assert isinstance(response.data["token_count_naive"], int)
        assert isinstance(response.data["token_count_efficient"], int)

        # --- No findings generated (Phase 5 constraint) ---
        assert response.new_findings == []

    def test_run_analysis_dispatch(self) -> None:
        dispatcher = _make_dispatcher()
        task = Task(
            task_id="TASK-006",
            action="RUN_ANALYSIS",
            target="https://example.com/login",
            context={},
            priority="high",
        )

        response = asyncio.run(dispatcher.dispatch(task))

        assert response.status == "success"
        assert response.worker == "analysis"
        assert response.new_findings[0]["type"] == "missing_csrf"

    def test_generate_report_dispatch(self) -> None:
        dispatcher = _make_dispatcher()
        task = Task(
            task_id="TASK-007",
            action="GENERATE_REPORT",
            target="https://example.com",
            context={
                "mission_id": "MISSION-001",
                "target_url": "https://example.com",
                "findings": [],
                "features": [],
                "routes": [],
            },
            priority="high",
        )

        response = asyncio.run(dispatcher.dispatch(task))

        assert response.status == "success"
        assert response.worker == "report"
        assert response.data["report_id"] == "REPORT-001"
        assert response.new_findings == []
