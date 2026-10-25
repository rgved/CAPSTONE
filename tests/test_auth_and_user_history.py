"""
tests/test_auth_and_user_history.py

Tests for:
1. User registration (signup) and login.
2. Token generation and validation.
3. Mission history isolation by user.
"""
import pytest
from pathlib import Path
from backend.memory.sqlite.database import init_db
from backend.services.storage_service import save_mission, get_mission
from backend.api.routes.auth import signup, login, get_current_user_from_header, SignUpRequest, LoginRequest
from backend.api.routes.missions import get_missions

@pytest.fixture
def auth_db(tmp_path: Path):
    db_file = tmp_path / "test_auth.db"
    init_db(db_path=str(db_file))
    return str(db_file)

def test_signup_and_login_flow(auth_db, monkeypatch):
    import backend.config as cfg
    import backend.memory.sqlite.database as db_mod
    monkeypatch.setattr(cfg, "DB_PATH", auth_db)
    monkeypatch.setattr(db_mod, "DB_PATH", auth_db)

    # 1. Sign up new user
    req = SignUpRequest(username="alice", email="alice@security.io", password="SecretPassword123!")
    res = signup(req)
    assert res["user"]["username"] == "alice"
    assert "token" in res

    # 2. Duplicate signup should fail
    with pytest.raises(Exception):
        signup(req)

    # 3. Login with correct password
    login_req = LoginRequest(username_or_email="alice", password="SecretPassword123!")
    login_res = login(login_req)
    token = login_res["token"]
    assert token

    # 4. Login with wrong password should fail
    bad_req = LoginRequest(username_or_email="alice", password="WrongPassword")
    with pytest.raises(Exception):
        login(bad_req)

    # 5. Token validation
    user = get_current_user_from_header(f"Bearer {token}")
    assert user is not None
    assert user["username"] == "alice"

def test_user_history_isolation(auth_db, monkeypatch):
    import backend.config as cfg
    import backend.memory.sqlite.database as db_mod
    monkeypatch.setattr(cfg, "DB_PATH", auth_db)
    monkeypatch.setattr(db_mod, "DB_PATH", auth_db)

    # Create two users
    alice_res = signup(SignUpRequest(username="alice", email="alice@test.com", password="PassAlice123!"))
    bob_res = signup(SignUpRequest(username="bob", email="bob@test.com", password="PassBob123!"))

    # Save missions for alice
    save_mission(
        mission_id="M-ALICE-1",
        target_url="https://alice-target.com",
        status="completed",
        username="alice",
        db_path=auth_db
    )
    # Save missions for bob
    save_mission(
        mission_id="M-BOB-1",
        target_url="https://bob-target.com",
        status="completed",
        username="bob",
        db_path=auth_db
    )

    # Alice requests mission list
    alice_missions = get_missions(authorization=f"Bearer {alice_res['token']}")
    assert len(alice_missions) == 1
    assert alice_missions[0]["mission_id"] == "M-ALICE-1"
    assert alice_missions[0]["target_url"] == "https://alice-target.com"

    # Bob requests mission list
    bob_missions = get_missions(authorization=f"Bearer {bob_res['token']}")
    assert len(bob_missions) == 1
    assert bob_missions[0]["mission_id"] == "M-BOB-1"
    assert bob_missions[0]["target_url"] == "https://bob-target.com"

def test_google_auth_signup_and_signin(auth_db, monkeypatch):
    from backend.api.routes.auth import google_auth, GoogleAuthRequest
    import backend.config as cfg
    import backend.memory.sqlite.database as db_mod
    monkeypatch.setattr(cfg, "DB_PATH", auth_db)
    monkeypatch.setattr(db_mod, "DB_PATH", auth_db)

    # 1. Sign up/in new user with Google
    req = GoogleAuthRequest(
        email="carol@gmail.com",
        name="Carol Danvers",
        google_id="google-sub-12345",
        avatar_url="https://lh3.googleusercontent.com/a/photo.jpg"
    )
    res = google_auth(req)
    assert "token" in res
    assert res["user"]["email"] == "carol@gmail.com"
    assert res["user"]["auth_provider"] == "google"
    token1 = res["token"]

    # 2. Re-authenticating with the same Google account returns same user
    res2 = google_auth(req)
    assert res2["user"]["id"] == res["user"]["id"]
    assert res2["user"]["email"] == "carol@gmail.com"

    # 3. Can query missions using this Google token
    save_mission(
        mission_id="M-CAROL-1",
        target_url="https://carol-security.io",
        status="completed",
        username=res["user"]["username"],
        db_path=auth_db
    )
    carol_missions = get_missions(authorization=f"Bearer {token1}")
    assert len(carol_missions) == 1
    assert carol_missions[0]["mission_id"] == "M-CAROL-1"


def test_new_user_starts_empty_and_ria_has_history(auth_db, monkeypatch):
    from backend.api.routes.auth import google_auth, GoogleAuthRequest, signup, SignUpRequest
    from backend.api.routes.missions import get_missions
    from backend.api.routes.dashboard import get_dashboard_summary
    from backend.api.routes.findings import get_findings_list
    from backend.api.routes.reports import get_reports_list
    from backend.api.routes.metrics import get_metrics_summary
    from backend.models.finding import Finding
    from backend.services.storage_service import save_finding, save_report
    from backend.models.security_report import SecurityReport, ReportFinding
    from datetime import datetime, timezone
    import backend.config as cfg
    import backend.memory.sqlite.database as db_mod

    monkeypatch.setattr(cfg, "DB_PATH", auth_db)
    monkeypatch.setattr(db_mod, "DB_PATH", auth_db)

    # 1. Sign up/in Ria Parmar
    ria_auth = google_auth(GoogleAuthRequest(
        email="riaaparmar5812@gmail.com",
        name="Ria Parmar",
        google_id="google-ria-001"
    ))
    ria_token = ria_auth["token"]
    ria_username = ria_auth["user"]["username"]

    # Save historical missions and findings for ria_parmar
    save_mission(
        mission_id="MISSION-001",
        target_url="https://ria-target.com",
        status="completed",
        username=ria_username,
        db_path=auth_db
    )
    save_finding(
        Finding(
            route_id=1,
            type="missing_csrf",
            title="CSRF Token Missing",
            feature="Authentication",
            severity="high",
            security_confidence=0.9,
            evidence=["form action=/login"]
        ),
        mission_id="MISSION-001",
        db_path=auth_db
    )
    save_report(
        SecurityReport(
            report_id="REP-001",
            mission_id="MISSION-001",
            target_url="https://ria-target.com",
            generated_at=datetime.now(timezone.utc),
            executive_summary="Summary",
            coverage_summary="Coverage",
            findings=[
                ReportFinding(
                    finding_id="F-001",
                    title="CSRF Missing",
                    category="missing_csrf",
                    severity="high",
                    confidence=0.9,
                    feature="Authentication"
                )
            ]
        ),
        db_path=auth_db
    )

    # 2. Check Ria's data across all endpoints
    ria_auth_hdr = f"Bearer {ria_token}"
    assert len(get_missions(authorization=ria_auth_hdr)) == 1
    ria_dash = get_dashboard_summary(authorization=ria_auth_hdr)
    assert ria_dash["stats"]["total_missions"] == 1
    assert ria_dash["stats"]["total_findings"] == 1
    assert len(ria_dash["recent_missions"]) == 1
    assert len(get_findings_list(authorization=ria_auth_hdr)) == 2
    assert len(get_reports_list(authorization=ria_auth_hdr)) == 1
    ria_metrics = get_metrics_summary(authorization=ria_auth_hdr)
    assert ria_metrics["total_missions"] == 1
    assert ria_metrics["total_findings"] == 1

    # 3. Sign up a completely new user
    new_auth = signup(SignUpRequest(
        username="fresh_analyst",
        email="fresh_analyst@company.org",
        password="SecurePass999!"
    ))
    new_token = new_auth["token"]
    new_auth_hdr = f"Bearer {new_token}"

    # 4. Verify new user has ZERO history across ALL endpoints
    assert get_missions(authorization=new_auth_hdr) == []
    new_dash = get_dashboard_summary(authorization=new_auth_hdr)
    assert new_dash["stats"]["total_missions"] == 0
    assert new_dash["stats"]["total_findings"] == 0
    assert new_dash["recent_missions"] == []
    assert all(item["count"] == 0 for item in new_dash["findings_severity"])
    assert get_findings_list(authorization=new_auth_hdr) == []
    assert get_reports_list(authorization=new_auth_hdr) == []
    new_metrics = get_metrics_summary(authorization=new_auth_hdr)
    assert new_metrics["total_missions"] == 0
    assert new_metrics["total_findings"] == 0
    assert new_metrics["token_reduction_by_mission"] == []

    # 5. When new user runs their own mission, only their mission is visible to them
    save_mission(
        mission_id="MISSION-002",
        target_url="https://fresh-target.org",
        status="completed",
        username="fresh_analyst",
        db_path=auth_db
    )
    new_missions = get_missions(authorization=new_auth_hdr)
    assert len(new_missions) == 1
    assert new_missions[0]["mission_id"] == "MISSION-002"

    # Ria still only sees MISSION-001, not MISSION-002
    ria_missions = get_missions(authorization=ria_auth_hdr)
    assert len(ria_missions) == 1
    assert ria_missions[0]["mission_id"] == "MISSION-001"


