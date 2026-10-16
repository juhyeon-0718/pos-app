"""
인증 스텁 (B1 범위). 실제 JWT/tableToken 발급·검증은 B2 이후.
- X-Table-Session-Token: 손님 세션. 스텁에서는 헤더 값 자체를 table_id로 쓴다.
- Authorization: Bearer <role>:<user_id> 형태의 가짜 토큰. 스텁에서는 role을 그대로 파싱한다.
  예) "Bearer owner:u_1" -> role=owner, user_id=u_1
실제 인증이 들어오면 이 모듈만 교체하면 되도록 함수 시그니처를 유지한다.
"""
from fastapi import Header, HTTPException

from app.models.enums import Role


def get_table_id(x_table_session_token: str | None = Header(default=None, alias="X-Table-Session-Token")) -> str:
    if not x_table_session_token:
        raise HTTPException(status_code=401, detail="X-Table-Session-Token 헤더가 필요합니다")
    return x_table_session_token


def get_current_role(authorization: str | None = Header(default=None)) -> Role:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authorization 헤더가 필요합니다")
    raw = authorization.split(" ", 1)[1]
    role_str = raw.split(":", 1)[0].strip()
    try:
        return Role(role_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="알 수 없는 role입니다") from None
