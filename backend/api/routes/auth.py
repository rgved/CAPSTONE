from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone
import hashlib
import hmac
import json
import base64
import time
import secrets
import logging

from backend.memory.sqlite.database import get_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "capstone_recon_secret_key_change_in_prod"


# ── Token Helpers ─────────────────────────────────────────────────────────────

def _generate_token(user_id: int, username: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "exp": int(time.time()) + 86400 * 7  # 7 days
    }
    raw_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), raw_payload.encode(), hashlib.sha256).hexdigest()
    return f"{raw_payload}.{signature}"


def verify_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        raw_payload, sig = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), raw_payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(raw_payload.encode()).decode())
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception as e:
        logger.debug("Token verification error: %s", e)
        return None


def get_current_user_from_header(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization or not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:].strip()
    return verify_token(token)


# ── Schemas ───────────────────────────────────────────────────────────────────

class SignUpRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignUpRequest):
    username = payload.username.strip()
    email = payload.email.strip().lower()
    password = payload.password

    if not username or len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long."
        )

    if not email or "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid email address is required."
        )

    if not password or len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Check if username or email exists
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        existing = cursor.fetchone()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with that username or email already exists."
            )

        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        created_at = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            "INSERT INTO users (username, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, email, password_hash, salt, created_at)
        )
        conn.commit()
        user_id = cursor.lastrowid

        token = _generate_token(user_id, username, email)
        return {
            "token": token,
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "created_at": created_at
            }
        }
    finally:
        conn.close()


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    identifier = payload.username_or_email.strip()
    password = payload.password

    if not identifier or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username/email and password are required."
        )

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, salt, created_at FROM users WHERE username = ? OR email = ?",
            (identifier, identifier.lower())
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password."
            )

        salt = user["salt"]
        expected_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        if not hmac.compare_digest(user["password_hash"], expected_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password."
            )

        token = _generate_token(user["id"], user["username"], user["email"])
        return {
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"]
            }
        }
    finally:
        conn.close()


@router.get("/me")
def me(authorization: Optional[str] = Header(None)):
    user_payload = get_current_user_from_header(authorization)
    if not user_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated."
        )

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = ?",
            (user_payload["user_id"],)
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "created_at": user["created_at"]
        }
    finally:
        conn.close()
