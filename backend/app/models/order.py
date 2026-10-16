from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, gen_id
from app.models.enums import OrderStatus


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: gen_id("o"))
    table_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, default=OrderStatus.received.value, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: gen_id("oi"))
    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.id"), nullable=False, index=True)
    menu_id: Mapped[str] = mapped_column(String, ForeignKey("menus.id"), nullable=False)
    menu_name: Mapped[str] = mapped_column(String, nullable=False)
    qty: Mapped[int] = mapped_column(nullable=False)
    price_snapshot: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    item_status: Mapped[str] = mapped_column(String, default="pending", nullable=False)

    order: Mapped[Order] = relationship("Order", back_populates="items")
