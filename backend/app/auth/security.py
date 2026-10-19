"""비밀번호 해시(pbkdf2_hmac)와 JWT 발급·검증.

외부 비밀값(JWT_SECRET)은 app.config에서만 읽는다. 추가 네이티브 의존성(bcrypt 등)
설치 부담을 줄이기 위해 표준 라이브러리 hashlib.pbkdf2_hmac을 쓴다.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.config import JWT_SECRET

_PBKDF2_ITERATIONS = 260_000
_ALGORITHM = "HS256"

ACCESS_TOKEN_TTL = timedelta(hours=12)
TABLE_SESSION_TOKEN_TTL = timedelta(hours=4)  # D-03: 4시간 만료
STREAM_TOKEN_TTL = timedelta(minutes=5)


def hash_password(raw_password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", raw_password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"pbkdf2$sha256${_PBKDF2_ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(raw_password: str, stored_hash: str) -> bool:
    try:
        scheme, algo, iterations_str, salt_b64, digest_b64 = stored_hash.split("$")
    except ValueError:
        return False
    if scheme != "pbkdf2":
        return False
    salt = base64.b64decode(salt_b64)
    expected = base64.b64decode(digest_b64)
    actual = hashlib.pbkdf2_hmac(algo, raw_password.encode("utf-8"), salt, int(iterations_str))
    return hmac.compare_digest(actual, expected)


def _encode(payload: dict[str, Any], ttl: timedelta) -> str:
    now = datetime.now(timezone.utc)
    full_payload = {**payload, "iat": int(now.timestamp()), "exp": int((now + ttl).timestamp())}
    return jwt.encode(full_payload, JWT_SECRET, algorithm=_ALGORITHM)


def _decode(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[_ALGORITHM])


def create_access_token(*, user_id: str, role: str) -> str:
    """직원/주방/사장 로그인 토큰 (bearerAuth)."""
    return _encode({"sub": user_id, "role": role, "type": "access"}, ACCESS_TOKEN_TTL)


def decode_access_token(token: str) -> dict[str, Any]:
    payload = _decode(token)
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("not an access token")
    return payload


def create_table_session_token(*, table_id: str, qr_token: str) -> str:
    """손님 테이블 세션 토큰. qr_token을 서명에 포함해 QR 재발급 시 자동 무효화된다 (D-03)."""
    return _encode({"table_id": table_id, "qr_token": qr_token, "type": "table_session"}, TABLE_SESSION_TOKEN_TTL)


def decode_table_session_token(token: str) -> dict[str, Any]:
    payload = _decode(token)
    if payload.get("type") != "table_session":
        raise jwt.InvalidTokenError("not a table session token")
    return payload


def create_stream_token(*, user_id: str, role: str) -> str:
    """SSE `/stream/orders`용 단기 토큰 (B-03 계약, 만료 5분)."""
    return _encode({"sub": user_id, "role": role, "type": "stream"}, STREAM_TOKEN_TTL)


def decode_stream_token(token: str) -> dict[str, Any]:
    payload = _decode(token)
    if payload.get("type") != "stream":
        raise jwt.InvalidTokenError("not a stream token")
    return payload
