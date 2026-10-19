"""다른 모듈이 의존하는 인증 디펜던시. auth_stub.py를 대체한다 (B-05, D-22).

함수 시그니처는 auth_stub과 동일하게 유지해 호출부(orders/kitchen 등)의 변경을
import 한 줄로 최소화한다. 다른 모듈은 이 파일만 의존하고 app.auth.models/
repository/service를 직접 import하지 않는다.
"""
import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.auth import repository
from app.auth.security import decode_access_token, decode_stream_token, decode_table_session_token
from app.db import get_db
from app.models.enums import Role


def get_table_id(
    x_table_session_token: str | None = Header(default=None, alias="X-Table-Session-Token"),
    db: Session = Depends(get_db),
) -> str:
    if not x_table_session_token:
        raise HTTPException(status_code=401, detail="X-Table-Session-Token 헤더가 필요합니다")
    try:
        payload = decode_table_session_token(x_table_session_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="테이블 세션이 만료되었습니다") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 테이블 세션 토큰입니다") from None

    table_id = payload["table_id"]
    table = repository.get_table_by_id(db, table_id)
    # QR 재발급 시 qr_token이 바뀌므로, 토큰이 가진 qr_token과 현재 값이 다르면 즉시 무효 (D-03).
    if table is None or table.qr_token != payload["qr_token"]:
        raise HTTPException(status_code=401, detail="테이블 세션이 더 이상 유효하지 않습니다(QR 재발급됨)") from None
    return table_id


class CurrentUser:
    def __init__(self, user_id: str, role: Role):
        self.user_id = user_id
        self.role = role


def _decode_bearer(authorization: str | None) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authorization 헤더가 필요합니다")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from None
    try:
        role = Role(payload["role"])
    except ValueError:
        raise HTTPException(status_code=401, detail="알 수 없는 role입니다") from None
    return CurrentUser(user_id=payload["sub"], role=role)


def get_current_role(authorization: str | None = Header(default=None)) -> Role:
    return _decode_bearer(authorization).role


def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    return _decode_bearer(authorization)


def require_owner(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current.role != Role.owner:
        raise HTTPException(status_code=403, detail="사장 권한이 필요합니다")
    return current


def get_stream_role(token: str) -> Role:
    """`/stream/orders?token=` 단기 토큰 검증 (B-03 계약)."""
    try:
        payload = decode_stream_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="스트림 토큰이 만료되었습니다") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 스트림 토큰입니다") from None
    try:
        return Role(payload["role"])
    except ValueError:
        raise HTTPException(status_code=401, detail="알 수 없는 role입니다") from None


def require_any_auth(
    authorization: str | None = Header(default=None),
    x_table_session_token: str | None = Header(default=None, alias="X-Table-Session-Token"),
    db: Session = Depends(get_db),
) -> None:
    """메뉴 조회처럼 tableToken·bearerAuth 둘 다 허용하는 엔드포인트용 (B-03 계약).

    둘 중 하나라도 유효하면 통과. 둘 다 없거나 둘 다 무효면 401.
    """
    if x_table_session_token:
        get_table_id(x_table_session_token, db)
        return
    if authorization:
        get_current_role(authorization)
        return
    raise HTTPException(status_code=401, detail="인증이 필요합니다")
