from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, gen_id
from app.models.enums import StockMovementReason


class StockMovement(Base, TimestampMixin):
    """식재료 입출고 원장. 직접 UPDATE로 재고를 고치지 않고 증감만 쌓는다 (D-05)."""
    __tablename__ = "stock_movements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: gen_id("sm"))
    ingredient_id: Mapped[str] = mapped_column(String, ForeignKey("ingredients.id"), nullable=False, index=True)
    qty_delta: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)  # StockMovementReason 값
    ref_id: Mapped[str | None] = mapped_column(String, nullable=True)  # 보통 order_id

    @staticmethod
    def valid_reason(value: str) -> bool:
        return value in {r.value for r in StockMovementReason}
