"""
backend/orchestrator/orchestrator.py

Deterministic orchestrator extended for multi-page prioritized scanning and Phase 6 analysis.
"""
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse

from backend.memory.sqlite.database import init_db
from backend.models.recon_result import ReconResult
from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.security_report import SecurityReport
from backend.models.route import Route
from backend.models.task import Task
from backend.models.worker_response import WorkerResponse
from backend.memory.chroma.vector_store import SemanticMemoryStore
from backend.orchestrator.mission_state import MissionState
from backend.orchestrator.task_dispatcher import TaskDispatcher
from backend.services.logger import get_logger
from backend.services.risk_scorer import is_same_domain, normalize_url, prioritize_routes
from backend.services.storage_service import (
    save_feature,
    save_finding,
    save_route,
    save_report,
    save_task,
    update_task_status,
)

logger = get_logger(__name__)


class Orchestrator:
    def __init__(
        self,
        dispatcher: TaskDispatcher | None = None,
        db_path: Optional[str] = None,
        semantic_memory: SemanticMemoryStore | None = None,
        max_crawl_routes: int = 1,
    ) -> None:
        self._dispatcher = dispatcher or TaskDispatcher()
        self._db_path = db_path
        self._semantic_memory = semantic_memory or SemanticMemoryStore()
        self._max_crawl_routes = max_crawl_routes
        self._mission_counter = 0
        self._visited_urls: set[str] = set()
        self._pending_recon_urls: list[str] = []
        self.all_saved_routes: list[Route] = []
        self.all_saved_features: list[Feature] = []
        self.all_recon_data: list[dict] = []
        self.last_response: WorkerResponse | None = None
        self.last_recon_data: dict | None = None
        self.last_prioritized_routes: list[dict] = []
        self.last_saved_route: Route | None = None
        self.last_saved_feature: Feature | None = None
        self.last_saved_findings: list[Finding] = []
        self.last_report: SecurityReport | None = None
        # Stores the data dict from a successful RUN_EFFICIENT_FETCH WorkerResponse.
        self.last_efficient_fetch_data: dict | None = None
        self.last_analysis_data: dict | None = None

    def create_mission(self, url: str) -> MissionState:
        self._mission_counter += 1
        mission_id = f"MISSION-{self._mission_counter:03d}"
        return MissionState(mission_id=mission_id, target=url)

    def choose_next_task(self, mission: MissionState) -> Task:
        if not mission.coverage.recon_completed:
            target_url = self._pending_recon_urls.pop(0) if self._pending_recon_urls else mission.target
            return Task(action="RUN_RECON", target=target_url, context={}, priority="high")

        if not mission.features_extracted:
            recon_result = self._build_aggregated_recon_data()
            return Task(
                action="EXTRACT_FEATURES",
                target=mission.target,
                context={"recon_result": recon_result},
                priority="high",
            )

        if not mission.efficient_fetch_completed:
            # Build source text from aggregated recon data
            recon_text = str(self._build_aggregated_recon_data())
            return Task(
                action="RUN_EFFICIENT_FETCH",
                target=mission.target,
                context={"source_text": recon_text, "query_hint": "security relevant features"},
                priority="high",
            )

        if not mission.analysis_completed:
            return Task(
                action="RUN_ANALYSIS",
                target=mission.target,
                context=self._build_analysis_context(),
                priority="high",
            )

        if not mission.report_generated:
            return Task(
                action="GENERATE_REPORT",
                target=mission.target,
                context=self._build_report_context(mission),
                priority="high",
            )

        return Task(action="STOP", target=mission.target, context={}, priority="low")

    def update_state(self, mission: MissionState, task: Task, response: WorkerResponse) -> MissionState:
        mission.current_task_id = task.task_id
        self.last_response = response

        if response.status == "failure":
            if task.action == "RUN_RECON" and (self.all_saved_routes or self.all_recon_data):
                # We already have successfully scanned at least one route (e.g. root target).
                # Failure on a secondary sub-route should NOT abort the entire mission.
                logger.warning(
                    "Sub-route recon failed for %s: %s - continuing mission with collected recon data",
                    task.target,
                    response.errors,
                )
                self._visited_urls.add(task.target)
                if not self._pending_recon_urls:
                    mission.coverage.recon_completed = True
                return mission

            logger.error("Task %s failed with errors: %s", task.task_id, response.errors)
            with open("orchestrator_errors.log", "a") as f:
                f.write(f"Task {task.task_id} failed with errors: {response.errors}\n")
            mission.status = "failed"
            return mission

        if task.action == "RUN_RECON":
            self._visited_urls.add(task.target)
            self.last_recon_data = response.data
            if isinstance(response.data, dict):
                self.all_recon_data.append(response.data)
            saved_route = save_route(
                Route(url=task.target, discovered_at=datetime.now(timezone.utc)),
                db_path=self._db_path,
                mission_id=mission.mission_id,
            )
            self.last_saved_route = saved_route
            self.all_saved_routes.append(saved_route)
            recon_result = ReconResult.model_validate(response.data)
            self._semantic_memory.upsert_route(self.last_saved_route, recon_result=recon_result)

            # Discover and normalize candidates within domain boundaries strictly for mission target
            raw_links = response.data.get("links", []) if isinstance(response.data, dict) else []
            normalized_links: list[str] = []
            for link in raw_links:
                norm = normalize_url(task.target, link)
                if norm and is_same_domain(mission.target, norm) and norm not in self._visited_urls:
                    normalized_links.append(norm)

            candidate_urls = [u for u in ([task.target] + normalized_links) if is_same_domain(mission.target, u)]
            prioritized = prioritize_routes(candidate_urls, seed_url=mission.target)
            self.last_prioritized_routes = [r.model_dump() for r in prioritized]
            logger.info("Prioritized %d routes - top_risk=%.1f", len(self.last_prioritized_routes), self.last_prioritized_routes[0]["risk_score"] if self.last_prioritized_routes else 0.0)

            # Queue high-risk unvisited endpoints if recursive crawling is enabled
            if len(self._visited_urls) < self._max_crawl_routes:
                for risk_item in prioritized:
                    candidate_url = risk_item.url
                    if (
                        candidate_url not in self._visited_urls
                        and candidate_url not in self._pending_recon_urls
                        and len(self._visited_urls) + len(self._pending_recon_urls) < self._max_crawl_routes
                    ):
                        self._pending_recon_urls.append(candidate_url)

            # Recon stage completes once pending queue is exhausted
            if not self._pending_recon_urls:
                mission.coverage.recon_completed = True
            else:
                mission.coverage.recon_completed = False

        elif task.action == "EXTRACT_FEATURES":
            mission.features_extracted = True
            feature = Feature.model_validate(response.data)
            self.last_saved_feature = save_feature(feature, db_path=self._db_path, mission_id=mission.mission_id)
            self.all_saved_features.append(self.last_saved_feature)
            self._semantic_memory.upsert_feature(self.last_saved_feature)
        elif task.action == "RUN_EFFICIENT_FETCH":
            # The worker already ran efficient_fetch() and stored results in response.data.
            self.last_efficient_fetch_data = response.data
            mission.efficient_fetch_completed = True
            logger.info(
                "Efficient fetch complete - naive=%d efficient=%d",
                response.data.get("token_count_naive", 0),
                response.data.get("token_count_efficient", 0),
            )
        elif task.action == "RUN_ANALYSIS":
            self.last_analysis_data = response.data
            mission.analysis_completed = True
            self.last_saved_findings = []

            for finding_payload in response.new_findings:
                finding = Finding.model_validate(finding_payload)
                saved_finding = save_finding(finding, db_path=self._db_path, mission_id=mission.mission_id)
                self.last_saved_findings.append(saved_finding)
                self._semantic_memory.upsert_finding(saved_finding)
            logger.info("Analysis complete - findings=%d", len(self.last_saved_findings))
        elif task.action == "GENERATE_REPORT":
            mission.report_generated = True
            report_payload = response.data.get("report")
            report_id = response.data.get("report_id")
            if report_payload is not None:
                self.last_report = SecurityReport.model_validate(report_payload)
                if report_id and self.last_report.report_id != report_id:
                    self.last_report = self.last_report.model_copy(update={"report_id": report_id})
                self.last_report = save_report(self.last_report, db_path=self._db_path)
            logger.info("Report complete - report_id=%s", report_id)

        return mission

    async def run(self, url: str) -> MissionState:
        init_db(db_path=self._db_path)
        self._semantic_memory.initialize()
        self._visited_urls = set()
        self._pending_recon_urls = []
        self.all_saved_routes = []
        self.all_saved_features = []
        self.all_recon_data = []
        self.last_response = None
        self.last_recon_data = None
        self.last_prioritized_routes = []
        self.last_saved_route = None
        self.last_saved_feature = None
        self.last_saved_findings = []
        self.last_report = None
        self.last_efficient_fetch_data = None
        self.last_analysis_data = None
        mission = self.create_mission(url)
        from backend.services.storage_service import current_mission_id
        current_mission_id.set(mission.mission_id)
        logger.info("Mission created - mission_id=%s target=%s", mission.mission_id, url)


        while mission.status == "running":
            task = self.choose_next_task(mission)
            saved_task = save_task(task, db_path=self._db_path)
            mission.current_task_id = saved_task.task_id

            if saved_task.action == "STOP":
                update_task_status(saved_task.task_id, "completed", db_path=self._db_path)
                mission.status = "completed"
                break

            response = await self._dispatcher.dispatch(saved_task)
            task_status = "completed" if response.status == "success" else "failed"
            update_task_status(saved_task.task_id, task_status, db_path=self._db_path)
            mission = self.update_state(mission, saved_task, response)

        if mission.status == "failed":
            self._record_stop_task(mission)
        logger.info("Mission finished - mission_id=%s status=%s", mission.mission_id, mission.status)
        return mission

    def _record_stop_task(self, mission: MissionState) -> None:
        stop_task = save_task(
            Task(action="STOP", target=mission.target, context={}, priority="low"),
            db_path=self._db_path,
        )
        update_task_status(stop_task.task_id, "completed", db_path=self._db_path)

    def _build_analysis_context(self) -> dict:
        feature_name = self.last_saved_feature.name if self.last_saved_feature is not None else ""
        similar_routes: list[dict] = []
        similar_features: list[dict] = []
        previous_findings: list[dict] = []

        if hasattr(self._semantic_memory, "search_routes"):
            try:
                similar_routes = [
                    result.model_dump() for result in self._semantic_memory.search_routes(feature_name, limit=3)
                ]
            except Exception:
                similar_routes = []

        if hasattr(self._semantic_memory, "search_features"):
            try:
                similar_features = [
                    result.model_dump() for result in self._semantic_memory.search_features(feature_name, limit=3)
                ]
            except Exception:
                similar_features = []

        if hasattr(self._semantic_memory, "search_findings"):
            try:
                previous_findings = [
                    result.model_dump() for result in self._semantic_memory.search_findings(feature_name, limit=3)
                ]
            except Exception:
                previous_findings = []

        return {
            "feature": self.last_saved_feature.model_dump() if self.last_saved_feature is not None else {},
            "recon_result": self._build_aggregated_recon_data(),
            "efficient_fetch_result": self.last_efficient_fetch_data or {},
            "route_id": self.last_saved_route.route_id if self.last_saved_route is not None else None,
            "semantic_context": {
                "similar_routes": similar_routes,
                "similar_features": similar_features,
                "previous_findings": previous_findings,
            },
        }

    def _build_aggregated_recon_data(self) -> dict[str, Any]:
        if not self.all_recon_data:
            return self.last_recon_data or {}

        all_forms = []
        all_inputs = []
        all_input_fields = []
        all_buttons = []
        all_scripts = []
        all_inline_scripts = []
        all_links = []
        all_meta_tags = []
        all_comments = []
        headers = {}
        status_code = 200
        url = ""

        seen_inputs: set[str] = set()
        seen_buttons: set[str] = set()
        seen_links: set[str] = set()
        seen_scripts: set[str] = set()

        for recon in self.all_recon_data:
            if not isinstance(recon, dict):
                continue
            if not url and recon.get("url"):
                url = recon.get("url", "")
            if recon.get("headers") and not headers:
                headers = recon.get("headers", {})
            if recon.get("status_code"):
                status_code = recon.get("status_code", 200)

            for f in recon.get("forms", []):
                all_forms.append(f)
            for inp in recon.get("inputs", []):
                if inp and inp not in seen_inputs:
                    seen_inputs.add(inp)
                    all_inputs.append(inp)
            for inf in recon.get("input_fields", []):
                all_input_fields.append(inf)
            for b in recon.get("buttons", []):
                if b and b not in seen_buttons:
                    seen_buttons.add(b)
                    all_buttons.append(b)
            for s in recon.get("scripts", []):
                if s and s not in seen_scripts:
                    seen_scripts.add(s)
                    all_scripts.append(s)
            for ins in recon.get("inline_scripts", []):
                all_inline_scripts.append(ins)
            for lk in recon.get("links", []):
                if lk and lk not in seen_links:
                    seen_links.add(lk)
                    all_links.append(lk)
            for m in recon.get("meta_tags", []):
                all_meta_tags.append(m)
            for c in recon.get("comments", []):
                all_comments.append(c)

        return {
            "url": url or (self.last_saved_route.url if self.last_saved_route else ""),
            "forms": all_forms,
            "inputs": all_inputs,
            "input_fields": all_input_fields,
            "buttons": all_buttons,
            "scripts": all_scripts,
            "inline_scripts": all_inline_scripts,
            "links": all_links,
            "meta_tags": all_meta_tags,
            "headers": headers,
            "status_code": status_code,
            "comments": all_comments,
        }

    def _build_report_context(self, mission: MissionState) -> dict:
        routes_to_report = self.all_saved_routes if self.all_saved_routes else ([self.last_saved_route] if self.last_saved_route else [])
        features_to_report = self.all_saved_features if self.all_saved_features else ([self.last_saved_feature] if self.last_saved_feature else [])
        return {
            "mission_id": mission.mission_id,
            "target_url": mission.target,
            "findings": [finding.model_dump() for finding in self.last_saved_findings],
            "features": [f.model_dump() for f in features_to_report],
            "routes": [r.model_dump() for r in routes_to_report],
            "prioritized_attack_surface": self.last_prioritized_routes,
            "recon_result": self._build_aggregated_recon_data(),
        }
