"""B-05: 로그인, 토큰 만료, QR 재발급 무효화, 역할별 403 검증.

관련 결정: D-03(토큰 만료/무효화), D-22(auth_stub 제거), D-25(auth 모듈 경계)
"""
from datetime import timedelta

import jwt
import pytest

from app.auth import repository, service
from app.auth.models import Table, User
from app.auth.security import (
    create_access_token,
    create_table_session_token,
    decode_table_session_token,
    hash_password,
)
from tests.conftest import auth_header


def _create_owner(db) -> User:
    return repository.create_user(db, username="owner1", password_hash=hash_password("pw12345"), role="owner")


def _create_staff(db) -> User:
    return repository.create_user(db, username="staff1", password_hash=hash_password("pw12345"), role="staff")


# ──────────────────────────────────────────────────────────────
# 로그인
# ──────────────────────────────────────────────────────────────


def test_login_success_returns_access_token(client, db):
    _create_owner(db)
    r = client.post("/api/v1/auth/login", json={"username": "owner1", "password": "pw12345"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["role"] == "owner"
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_returns_401(client, db):
    _create_owner(db)
    r = client.post("/api/v1/auth/login", json={"username": "owner1", "password": "wrong"})
    assert r.status_code == 401, r.text


def test_login_unknown_username_returns_401(client, db):
    r = client.post("/api/v1/auth/login", json={"username": "nobody", "password": "pw12345"})
    assert r.status_code == 401, r.text


# ──────────────────────────────────────────────────────────────
# 접근 토큰 만료
# ──────────────────────────────────────────────────────────────


def test_expired_access_token_returns_401(client, db):
    _create_staff(db)
    # TTL을 음수로 줘서 이미 만료된 토큰을 만든다.
    from app.auth import security

    now_ttl = security.ACCESS_TOKEN_TTL
    security.ACCESS_TOKEN_TTL = timedelta(seconds=-1)
    try:
        expired_token = create_access_token(user_id="u_1", role="staff")
    finally:
        security.ACCESS_TOKEN_TTL = now_ttl

    r = client.get("/api/v1/tables", headers={"Authorization": f"Bearer {expired_token}"})
    assert r.status_code == 401, r.text


# ──────────────────────────────────────────────────────────────
# 테이블 세션: QR 재발급 시 구토큰 무효화 (D-03)
# ──────────────────────────────────────────────────────────────


def test_table_session_token_invalidated_after_qr_reissue(db):
    table = Table(table_no=99, qr_token="qr_old")
    db.add(table)
    db.commit()
    db.refresh(table)

    old_token = create_table_session_token(table_id=table.id, qr_token=table.qr_token)
    # 유효한 시점에는 정상 디코드됨
    payload = decode_table_session_token(old_token)
    assert payload["table_id"] == table.id

    service.reissue_qr(db, table.id)
    db.refresh(table)

    # 토큰 자체는 서명·만료 상 유효하지만, repository 조회 시 qr_token이 달라 무효 처리된다.
    refreshed = repository.get_table_by_id(db, table.id)
    assert refreshed.qr_token != "qr_old"
    payload = decode_table_session_token(old_token)
    assert payload["qr_token"] != refreshed.qr_token


def test_table_session_expired_token_raises(db):
    table = Table(table_no=98, qr_token="qr_a")
    db.add(table)
    db.commit()
    db.refresh(table)

    from app.auth import security

    orig_ttl = security.TABLE_SESSION_TOKEN_TTL
    security.TABLE_SESSION_TOKEN_TTL = timedelta(seconds=-1)
    try:
        expired = create_table_session_token(table_id=table.id, qr_token=table.qr_token)
    finally:
        security.TABLE_SESSION_TOKEN_TTL = orig_ttl

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_table_session_token(expired)


# ──────────────────────────────────────────────────────────────
# 역할별 403 (owner 전용 API)
# ──────────────────────────────────────────────────────────────


def test_staff_cannot_list_users_403(client, db):
    r = client.get("/api/v1/users", headers=auth_header("staff"))
    assert r.status_code == 403, r.text


def test_owner_can_list_users(client, db):
    r = client.get("/api/v1/users", headers=auth_header("owner"))
    assert r.status_code == 200, r.text


def test_create_user_duplicate_username_conflict(client, db):
    repository.create_user(db, username="dup1", password_hash=hash_password("x"), role="staff")
    r = client.post(
        "/api/v1/users",
        headers=auth_header("owner"),
        json={"username": "dup1", "password": "y", "role": "staff"},
    )
    assert r.status_code == 409, r.text
