from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import gen_id, utcnow


class User(Base):
    """직원/주방/사장 로그인 계정 (D-03, D-23)."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: gen_id("u"))
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Table(Base):
    """매장 테이블. qr_token이 바뀌면(재발급) 그 시점 이전 세션 토큰은 모두 무효화된다 (D-03)."""

    __tablename__ = "tables"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: gen_id("t"))
    table_no: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    qr_token: Mapped[str] = mapped_column(String, nullable=False, default=lambda: gen_id("qr"))
    qr_issued_at: Mapped[object] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
