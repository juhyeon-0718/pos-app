from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import gen_id


class Ingredient(Base):
    """
    식재료 원장 대상. 현재고는 이 테이블에 저장하지 않고 stock_movements 원장의
    합계로 계산한다 (D-05: 원장 합계 = 현재 재고). safety_stock/lead_time_days는
    발주 추천(B2 이후)에서 쓴다. unit_price는 발주 추천 estimated_cost 계산에 쓴다 (B-03).
    is_active=false는 비활성화된 식재료(목록·발주 추천에서 제외, B-06).
    """
    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: gen_id("ing"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    safety_stock: Mapped[float] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
