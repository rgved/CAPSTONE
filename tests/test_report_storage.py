from datetime import datetime, timezone

from backend.memory.sqlite.database import init_db
from backend.models.security_report import SecurityReport
from backend.services.storage_service import get_report, save_report


class TestReportStorage:
    def test_save_report_assigns_report_id(self, tmp_path) -> None:
        db_path = str(tmp_path / "report_storage.db")
        init_db(db_path=db_path)

        saved = save_report(
            SecurityReport(
                report_id=None,
                mission_id="MISSION-001",
                target_url="https://example.com",
                generated_at=datetime.now(timezone.utc),
                executive_summary="Summary",
                coverage_summary="Coverage",
                severity_breakdown={"High": 0, "Medium": 1, "Low": 0, "Informational": 0},
                findings=[],
                recommendations=[],
                statistics={"routes_discovered": 1, "features_identified": 1, "findings_generated": 1},
            ),
            db_path=db_path,
        )

        assert saved.report_id == "REPORT-001"

    def test_get_report_returns_latest_report(self, tmp_path) -> None:
        db_path = str(tmp_path / "report_storage.db")
        init_db(db_path=db_path)

        save_report(
            SecurityReport(
                report_id=None,
                mission_id="MISSION-001",
                target_url="https://example.com",
                generated_at=datetime.now(timezone.utc),
                executive_summary="Summary",
                coverage_summary="Coverage",
                severity_breakdown={"High": 0, "Medium": 1, "Low": 0, "Informational": 0},
                findings=[],
                recommendations=[],
                statistics={"routes_discovered": 1, "features_identified": 1, "findings_generated": 1},
            ),
            db_path=db_path,
        )

        report = get_report(db_path=db_path)

        assert report is not None
        assert report.report_id == "REPORT-001"
        assert report.mission_id == "MISSION-001"
