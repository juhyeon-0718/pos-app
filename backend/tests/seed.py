"""SEED=42 고정 테스트 데이터 (D-12).

TC-01/TC-07 사전 조건:
- 메뉴A: 레시피에 재료X 2개 필요
- 재료X 초기 재고: 10개
"""
from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient
from app.models.menu import Menu
from app.models.recipe import RecipeItem
from app.models.stock_movement import StockMovement
from app.models.enums import StockMovementReason

# 고정 ID (SEED=42)
INGREDIENT_X_ID = "ing_seed42_x"
MENU_A_ID = "m_seed42_a"

INGREDIENT_X_INITIAL_STOCK: float = 10.0
RECIPE_QTY_PER_UNIT: float = 2.0  # 메뉴A 1개당 재료X 2개


def seed(db: Session) -> None:
    """DB에 SEED=42 기준 픽스처 데이터를 삽입하고 commit한다."""
    db.add(Ingredient(
        id=INGREDIENT_X_ID,
        name="재료X",
        unit="개",
        safety_stock=0,
        lead_time_days=0,
    ))
    # 초기 재고 10개
    db.add(StockMovement(
        ingredient_id=INGREDIENT_X_ID,
        qty_delta=INGREDIENT_X_INITIAL_STOCK,
        reason=StockMovementReason.restock.value,
        ref_id=None,
    ))
    db.add(Menu(
        id=MENU_A_ID,
        name="메뉴A",
        price=10000,
        category="main",
        is_active=True,
    ))
    db.add(RecipeItem(
        menu_id=MENU_A_ID,
        ingredient_id=INGREDIENT_X_ID,
        qty_per_unit=RECIPE_QTY_PER_UNIT,
        unit="개",
    ))
    db.commit()
