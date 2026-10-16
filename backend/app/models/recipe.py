from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import gen_id


class RecipeItem(Base):
    """메뉴 1개(1 qty 기준) 당 필요한 식재료 BOM 한 줄."""
    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: gen_id("rcp"))
    menu_id: Mapped[str] = mapped_column(String, ForeignKey("menus.id"), nullable=False, index=True)
    ingredient_id: Mapped[str] = mapped_column(String, ForeignKey("ingredients.id"), nullable=False, index=True)
    qty_per_unit: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
