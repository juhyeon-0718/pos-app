from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin


class IdempotencyKey(Base, TimestampMixin):
    """
    POST /orders 중복 생성 방지 (D-15). key는 클라이언트가 만든 UUID.
    request_hash는 재요청 본문이 최초 요청과 같은지 비교하는 용도 (다르면 422).
    24시간 보관 — 만료 정리는 배치/스케줄러로 별도 처리 (B1 범위 밖).
    """
    __tablename__ = "idempotency_keys"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    order_id: Mapped[str] = mapped_column(String, nullable=False)
    request_hash: Mapped[str] = mapped_column(String, nullable=False)
