"""
backend/services/storage_service.py

Persistence operations for Phase 1 and Phase 2 storage needs.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Optional
import contextvars

current_mission_id = contextvars.ContextVar("current_mission_id", default=None)

from backend.memory.sqlite.database import get_connection
from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.route import Route
from backend.models.security_report import SecurityReport
from backend.models.task import Task
from backend.services.logger import get_logger

logger = get_logger(__name__)


def save_route(route: Route, db_path: Optional[str] = None, mission_id: Optional[str] = None) -> Route:
    """
    Persist a Route to the routes table.

    Returns a copy of the route with route_id populated from SQLite.
    """
    conn = get_connection(db_path)
    m_id = mission_id or current_mission_id.get()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO routes (url, discovered_at, mission_id) VALUES (?, ?, ?)",
            (route.url, route.discovered_at.isoformat(), m_id),
        )
        conn.commit()
        assigned_id: int = cursor.lastrowid  # type: ignore[assignment]
        saved = route.model_copy(update={"route_id": assigned_id})
        logger.info("Route saved - id=%d url=%s mission_id=%s", assigned_id, route.url, m_id)
        return saved
    finally:
        conn.close()


def get_routes(db_path: Optional[str] = None) -> list[Route]:
    """
    Retrieve all routes from the routes table.

    Returns an empty list if no routes have been saved yet.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, url, discovered_at FROM routes ORDER BY id ASC")
        rows = cursor.fetchall()
        routes = [
            Route(
                route_id=row["id"],
                url=row["url"],
                discovered_at=datetime.fromisoformat(row["discovered_at"]),
            )
            for row in rows
        ]
        logger.info("Retrieved %d route(s)", len(routes))
        return routes
    finally:
        conn.close()


def save_feature(feature: Feature, db_path: Optional[str] = None, mission_id: Optional[str] = None) -> Feature:
    """Persist a Feature to the features table."""
    conn = get_connection(db_path)
    m_id = mission_id or current_mission_id.get()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO features (name, analyzed, routes, classification_confidence, mission_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                feature.name,
                int(feature.analyzed),
                json.dumps(feature.routes),
                feature.classification_confidence,
                m_id,
            ),
        )
        conn.commit()
        row_id: int = cursor.lastrowid  # type: ignore[assignment]
        saved = feature.model_copy(update={"feature_id": _format_feature_id(feature.name, row_id)})
        logger.info("Feature saved - id=%s name=%s mission_id=%s", saved.feature_id, saved.name, m_id)
        return saved
    finally:
        conn.close()


def get_features(db_path: Optional[str] = None) -> list[Feature]:
    """Retrieve all persisted features from SQLite."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, analyzed, routes, classification_confidence
            FROM features
            ORDER BY id ASC
            """
        )
        rows = cursor.fetchall()
        features = [
            Feature(
                feature_id=_format_feature_id(row["name"], row["id"]),
                name=row["name"],
                routes=json.loads(row["routes"] or "[]"),
                classification_confidence=float(row["classification_confidence"]),
                analyzed=bool(row["analyzed"]),
            )
            for row in rows
        ]
        logger.info("Retrieved %d feature(s)", len(features))
        return features
    finally:
        conn.close()


def save_finding(finding: Finding, db_path: Optional[str] = None, mission_id: Optional[str] = None) -> Finding:
    """Persist a Finding to the findings table."""
    conn = get_connection(db_path)
    m_id = mission_id or current_mission_id.get()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO findings (
                finding_id, type, title, feature, severity,
                security_confidence, evidence, description, reasoning, route_id, mission_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                finding.finding_id,
                finding.type,
                finding.title,
                finding.feature,
                finding.severity,
                finding.security_confidence,
                json.dumps(finding.evidence),
                finding.description,
                finding.reasoning,
                finding.route_id,
                m_id,
            ),
        )
        conn.commit()
        row_id: int = cursor.lastrowid  # type: ignore[assignment]
        saved = finding.model_copy(update={"finding_id": _format_finding_id(row_id)})
        cursor.execute(
            "UPDATE findings SET finding_id = ? WHERE id = ?",
            (saved.finding_id, row_id),
        )
        conn.commit()
        logger.info("Finding saved - id=%s title=%s severity=%s mission_id=%s", saved.finding_id, saved.title, saved.severity, m_id)
        return saved
    finally:
        conn.close()


def get_findings(db_path: Optional[str] = None) -> list[Finding]:
    """Retrieve all persisted findings from SQLite."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, finding_id, type, title, feature, severity,
                   security_confidence, evidence, description, reasoning, route_id
            FROM findings
            ORDER BY id ASC
            """
        )
        rows = cursor.fetchall()
        findings = [
            Finding(
                finding_id=row["finding_id"] or _format_finding_id(row["id"]),
                type=row["type"],
                title=row["title"],
                feature=row["feature"],
                severity=row["severity"],
                security_confidence=float(row["security_confidence"]),
                evidence=json.loads(row["evidence"] or "[]"),
                description=row["description"] or "",
                reasoning=row["reasoning"] if "reasoning" in row.keys() and row["reasoning"] else "",
                route_id=row["route_id"],
            )
            for row in rows
        ]
        logger.info("Retrieved %d finding(s)", len(findings))
        return findings
    finally:
        conn.close()


def save_report(report: SecurityReport, db_path: Optional[str] = None) -> SecurityReport:
    """Persist a SecurityReport to the reports table."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        report_json = report.model_dump_json()
        cursor.execute(
            """
            INSERT INTO reports (report_id, mission_id, target_url, generated_at, report_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                report.report_id,
                report.mission_id,
                report.target_url,
                report.generated_at.isoformat(),
                report_json,
            ),
        )
        conn.commit()
        row_id: int = cursor.lastrowid  # type: ignore[assignment]
        saved = report.model_copy(update={"report_id": _format_report_id(row_id)})
        cursor.execute(
            "UPDATE reports SET report_id = ?, report_json = ? WHERE id = ?",
            (saved.report_id, saved.model_dump_json(), row_id),
        )
        conn.commit()
        logger.info("Report saved - id=%s mission_id=%s", saved.report_id, saved.mission_id)
        return saved
    finally:
        conn.close()


def get_report(db_path: Optional[str] = None) -> SecurityReport | None:
    """Return the most recently stored report, if any."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT report_id, mission_id, target_url, generated_at, report_json
            FROM reports
            ORDER BY id DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if row is None:
            return None
        report = SecurityReport.model_validate_json(row["report_json"])
        if report.report_id is None:
            report = report.model_copy(update={"report_id": row["report_id"] or _format_report_id(1)})
        return report
    finally:
        conn.close()


def save_task(task: Task, db_path: Optional[str] = None) -> Task:
    """
    Persist a Task and assign its contract task_id.

    The SQLite schema stores an integer primary key. Phase 2 exposes that row
    as TASK-XXX without modifying the schema defined in contracts.md.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        mission_id = current_mission_id.get()
        cursor.execute(
            "INSERT INTO tasks (action, status, created_at, mission_id, target) VALUES (?, ?, ?, ?, ?)",
            (task.action, task.status, task.created_at.isoformat(), mission_id, task.target),
        )
        conn.commit()
        row_id: int = cursor.lastrowid  # type: ignore[assignment]
        saved = task.model_copy(update={"task_id": _format_task_id(row_id)})
        logger.info("Task saved - id=%s action=%s status=%s mission_id=%s target=%s", saved.task_id, saved.action, saved.status, mission_id, task.target)
        return saved
    finally:
        conn.close()


def update_task_status(task_id: str, status: str, db_path: Optional[str] = None) -> None:
    """Update the persisted status for a task identified by contract task_id."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, _parse_task_id(task_id)),
        )
        conn.commit()
        logger.info("Task updated - id=%s status=%s", task_id, status)
    finally:
        conn.close()


def get_tasks(db_path: Optional[str] = None) -> list[Task]:
    """Retrieve all persisted tasks in insertion order."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, action, status, created_at, mission_id, target FROM tasks ORDER BY id ASC")
        rows = cursor.fetchall()
        tasks = [
            Task(
                task_id=_format_task_id(row["id"]),
                action=row["action"],
                target=row["target"] if "target" in row.keys() and row["target"] else "",
                context={},
                priority="medium",
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                mission_id=row["mission_id"],
            )
            for row in rows
        ]
        logger.info("Retrieved %d task(s)", len(tasks))
        return tasks
    finally:
        conn.close()


def _format_task_id(row_id: int) -> str:
    return f"TASK-{row_id:03d}"


def _parse_task_id(task_id: str) -> int:
    prefix = "TASK-"
    if not task_id.startswith(prefix):
        raise ValueError(f"Invalid task_id format: {task_id}")
    return int(task_id[len(prefix):])


def _format_feature_id(feature_name: str, row_id: int) -> str:
    prefixes = {
        "authentication": "AUTH",
        "registration": "REG",
        "password_reset": "PWD",
        "search": "SEARCH",
        "file_upload": "UPLOAD",
        "api": "API",
        "user_profile": "PROFILE",
        "admin_panel": "ADMIN",
        "dashboard": "DASH",
        "settings": "SET",
        "unknown": "UNKNOWN",
    }
    prefix = prefixes[feature_name]
    return f"{prefix}-{row_id:03d}"


def _format_finding_id(row_id: int) -> str:
    return f"FIND-{row_id:03d}"


def _format_report_id(row_id: int) -> str:
    return f"REPORT-{row_id:03d}"
