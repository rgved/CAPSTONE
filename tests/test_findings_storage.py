from backend.memory.sqlite.database import init_db
from backend.models.finding import Finding
from backend.services.storage_service import get_findings, save_finding


class TestFindingStorage:
    def test_save_and_get_finding_round_trip(self, tmp_path) -> None:
        db_path = str(tmp_path / "findings.db")
        init_db(db_path=db_path)

        saved = save_finding(
            Finding(
                type="missing_csrf",
                title="Potential Missing CSRF Protection",
                feature="authentication",
                severity="low",
                security_confidence=0.82,
                evidence=["POST form detected", "No CSRF token observed"],
                description="The login flow appears to submit without an observed token.",
                route_id=1,
            ),
            db_path=db_path,
        )

        findings = get_findings(db_path=db_path)

        assert saved.finding_id == "FIND-001"
        assert len(findings) == 1
        assert findings[0].finding_id == "FIND-001"
        assert findings[0].type == "missing_csrf"
        assert findings[0].feature == "authentication"
        assert findings[0].severity == "low"
        assert findings[0].security_confidence == 0.82
        assert findings[0].evidence == ["POST form detected", "No CSRF token observed"]
