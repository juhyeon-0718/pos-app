from sqlalchemy import Boolean, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import gen_id


class Menu(Base):
    __tablename__ = "menus"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: gen_id("m"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # D-37: 소프트 삭제 표시. 값이 있으면 모든 목록·수정·주문에서 제외하고 과거 주문 참조는 유지한다.
    deleted_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=True)
