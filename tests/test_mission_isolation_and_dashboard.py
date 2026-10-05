"""
tests/test_mission_isolation_and_dashboard.py

Tests ensuring:
1. Unique, isolated findings and attack surfaces per mission and target URL.
2. Dashboard findings severity breakdown displays strictly vulnerability categories (High, Medium, Low) and excludes Informational.
"""
from datetime import datetime, timezone
import json
import pytest
from pathlib import Path
from backend.memory.sqlite.database import init_db, get_connection
from backend.models.route import Route
from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.security_report import SecurityReport, ReportFinding
from backend.services.storage_service import save_route, save_feature, save_finding, save_report
from backend.api.routes.missions import get_mission_routes, get_mission_detail, get_missions
from backend.api.routes.dashboard import get_dashboard_summary
from backend.api.routes.findings import get_findings_list

@pytest.fixture
def isolated_db(tmp_path: Path):
    db_file = tmp_path / "test_isolation.db"
    init_db(db_path=str(db_file))
    return str(db_file)

def test_dashboard_severity_bars_and_metrics(isolated_db, monkeypatch):
    import backend.config as cfg
    import backend.memory.sqlite.database as db_mod
    
    monkeypatch.setattr(cfg, "DB_PATH", isolated_db)
    monkeypatch.setattr(db_mod, "DB_PATH", isolated_db)
    
    now = datetime.now(timezone.utc)
    # Save routes and findings with different severities
    r1 = save_route(Route(url="https://site-a.com/login", discovered_at=now), db_path=isolated_db, mission_id="MISSION-001")
    save_finding(
        Finding(
            route_id=r1.route_id,
            type="missing_csrf",
            title="CSRF Token Missing",
            feature="Authentication",
            severity="high",
            security_confidence=0.9,
            evidence=["form action=/login"]
        ),
        db_path=isolated_db,
        mission_id="MISSION-001"
    )
    save_finding(
        Finding(
            route_id=r1.route_id,
            type="missing_security_headers",
            title="Missing CSP",
            feature="Configuration",
            severity="medium",
            security_confidence=0.8,
            evidence=["no CSP header"]
        ),
        db_path=isolated_db,
        mission_id="MISSION-001"
    )
    save_finding(
        Finding(
            route_id=r1.route_id,
            type="sensitive_input",
            title="Exposed Email Field",
            feature="Input",
            severity="low",
            security_confidence=0.7,
            evidence=["input email"]
        ),
        db_path=isolated_db,
        mission_id="MISSION-001"
    )
    save_finding(
        Finding(
            route_id=r1.route_id,
            type="unknown",
            title="Tech Stack Note",
            feature="Info",
            severity="informational",
            security_confidence=0.5,
            evidence=["detected nginx"]
        ),
        db_path=isolated_db,
        mission_id="MISSION-001"
    )
    
    summary = get_dashboard_summary()
    
    # 1. Total findings should exclude Informational
    assert summary["stats"]["total_findings"] == 3
    
    # 2. Findings severity list must only contain High, Medium, Low (no Informational)
    sev_categories = [item["severity"] for item in summary["findings_severity"]]
    assert sev_categories == ["High", "Medium", "Low"]
    
    sev_map = {item["severity"]: item["count"] for item in summary["findings_severity"]}
    assert sev_map["High"] == 1
    assert sev_map["Medium"] == 1
    assert sev_map["Low"] == 1

def test_mission_attack_surface_and_findings_isolation(isolated_db, monkeypatch):
    import backend.config as cfg
    import backend.memory.sqlite.database as db_mod
    monkeypatch.setattr(cfg, "DB_PATH", isolated_db)
    monkeypatch.setattr(db_mod, "DB_PATH", isolated_db)
    
    now = datetime.now(timezone.utc)
    # Create Mission 1 on site-a.com
    r_a1 = save_route(Route(url="https://site-a.com/login", discovered_at=now), db_path=isolated_db, mission_id="MISSION-001")
    r_a2 = save_route(Route(url="https://site-a.com/admin", discovered_at=now), db_path=isolated_db, mission_id="MISSION-001")
    f_a1 = save_finding(
        Finding(
            route_id=r_a1.route_id,
            type="weak_authentication",
            title="Site A Weak Auth",
            feature="Authentication",
            severity="high",
            security_confidence=0.9,
            evidence=["no lockout"]
        ),
        db_path=isolated_db,
        mission_id="MISSION-001"
    )
    
    # Create Mission 2 on site-b.com
    r_b1 = save_route(Route(url="https://site-b.com/upload", discovered_at=now), db_path=isolated_db, mission_id="MISSION-002")
    r_b2 = save_route(Route(url="https://site-b.com/profile", discovered_at=now), db_path=isolated_db, mission_id="MISSION-002")
    f_b1 = save_finding(
        Finding(
            route_id=r_b1.route_id,
            type="file_upload_risk",
            title="Site B Upload Risk",
            feature="File Upload",
            severity="high",
            security_confidence=0.85,
            evidence=["unrestricted upload"]
        ),
        db_path=isolated_db,
        mission_id="MISSION-002"
    )
    
    conn = get_connection(db_path=isolated_db)
    cursor = conn.cursor()
    
    # Check routes for site-a
    routes_a = get_mission_routes("https://site-a.com", {}, cursor, mission_id="MISSION-001")
    assert all("site-a.com" in u for u in routes_a)
    assert not any("site-b.com" in u for u in routes_a)
    assert "https://site-a.com/admin" in routes_a
    
    # Check routes for site-b
    routes_b = get_mission_routes("https://site-b.com", {}, cursor, mission_id="MISSION-002")
    assert all("site-b.com" in u for u in routes_b)
    assert not any("site-a.com" in u for u in routes_b)
    assert "https://site-b.com/upload" in routes_b
    
    conn.close()
    
    # Now check get_mission_detail for MISSION-001
    detail_a = get_mission_detail("MISSION-001")
    assert detail_a["mission_id"] == "MISSION-001"
    assert detail_a["target_url"] == "https://site-a.com/login"
    assert len(detail_a["findings"]) == 1
    assert detail_a["findings"][0]["title"] == "Site A Weak Auth"
    assert all("site-a.com" in ep["url"] for ep in detail_a["prioritized_attack_surface"])
    assert not any("site-b.com" in ep["url"] for ep in detail_a["prioritized_attack_surface"])
    
    # Check get_mission_detail for MISSION-002
    detail_b = get_mission_detail("MISSION-002")
    assert detail_b["mission_id"] == "MISSION-002"
    assert detail_b["target_url"] == "https://site-b.com/upload"
    assert len(detail_b["findings"]) == 1
    assert detail_b["findings"][0]["title"] == "Site B Upload Risk"
    assert all("site-b.com" in ep["url"] for ep in detail_b["prioritized_attack_surface"])
    assert not any("site-a.com" in ep["url"] for ep in detail_b["prioritized_attack_surface"])
