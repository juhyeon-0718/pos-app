"""auth 모듈의 업무 로직. 라우터는 이 모듈의 함수만 호출한다 (D-25)."""
from sqlalchemy.orm import Session

from app.auth import repository
from app.auth.models import Table, User
from app.auth.security import (
    create_access_token,
    create_stream_token,
    create_table_session_token,
    hash_password,
    verify_password,
)


class NotFound(Exception):
    pass


class Unauthorized(Exception):
    pass


class Conflict(Exception):
    pass


def login(db: Session, *, username: str, password: str) -> tuple[str, str]:
    """성공 시 (access_token, role) 반환, 실패 시 Unauthorized."""
    user = repository.get_user_by_username(db, username)
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise Unauthorized("아이디 또는 비밀번호가 올바르지 않습니다")
    token = create_access_token(user_id=user.id, role=user.role)
    return token, user.role


def issue_stream_token(*, user_id: str, role: str) -> str:
    return create_stream_token(user_id=user_id, role=role)


def list_users(db: Session) -> list[User]:
    return repository.list_users(db)


def create_user(db: Session, *, username: str, password: str, role: str) -> User:
    if repository.get_user_by_username(db, username) is not None:
        raise Conflict(f"이미 존재하는 username: {username}")
    return repository.create_user(db, username=username, password_hash=hash_password(password), role=role)


def update_user(db: Session, user_id: str, *, password: str | None, role: str | None, is_active: bool | None) -> User:
    user = repository.get_user_by_id(db, user_id)
    if user is None:
        raise NotFound(f"사용자를 찾을 수 없습니다: {user_id}")
    password_hash = hash_password(password) if password else None
    return repository.update_user(db, user, password_hash=password_hash, role=role, is_active=is_active)


def list_tables(db: Session) -> list[Table]:
    return repository.list_tables(db)


def create_table(db: Session, *, table_no: int) -> Table:
    return repository.create_table(db, table_no=table_no)


def create_table_session(db: Session, *, table_id: str, qr_token: str) -> str:
    """QR 토큰이 테이블의 현재 qr_token과 일치해야 세션 토큰을 발급한다 (D-03)."""
    table = repository.get_table_by_id(db, table_id)
    if table is None or table.qr_token != qr_token:
        raise Unauthorized("QR 토큰이 유효하지 않습니다")
    return create_table_session_token(table_id=table.id, qr_token=table.qr_token)


def reissue_qr(db: Session, table_id: str) -> Table:
    table = repository.get_table_by_id(db, table_id)
    if table is None:
        raise NotFound(f"테이블을 찾을 수 없습니다: {table_id}")
    return repository.reissue_qr(db, table)
