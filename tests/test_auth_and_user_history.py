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
