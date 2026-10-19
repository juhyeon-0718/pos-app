"""inventory 모듈 DB 접근 계층. ingredients/stock_movements 테이블만 다룬다 (D-25)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient
from app.models.recipe import RecipeItem
from app.models.stock_movement import StockMovement


def list_ingredients(db: Session) -> list[Ingredient]:
    return list(db.execute(select(Ingredient).order_by(Ingredient.id)).scalars().all())


def get_ingredient(db: Session, ingredient_id: str) -> Ingredient | None:
    return db.get(Ingredient, ingredient_id)


def create_ingredient(
    db: Session, *, name: str, unit: str, safety_stock: float, lead_time_days: int, unit_price: float
) -> Ingredient:
    ingredient = Ingredient(
        name=name, unit=unit, safety_stock=safety_stock, lead_time_days=lead_time_days, unit_price=unit_price
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


def update_ingredient(db: Session, ingredient: Ingredient, **fields) -> Ingredient:
    for key, value in fields.items():
        if value is not None:
            setattr(ingredient, key, value)
    db.commit()
    db.refresh(ingredient)
    return ingredient


def recipe_references_ingredient(db: Session, ingredient_id: str) -> bool:
    row = db.execute(select(RecipeItem.id).where(RecipeItem.ingredient_id == ingredient_id).limit(1)).first()
    return row is not None


def list_movements(db: Session, ingredient_id: str) -> list[StockMovement]:
    return list(
        db.execute(
            select(StockMovement)
            .where(StockMovement.ingredient_id == ingredient_id)
            .order_by(StockMovement.created_at)
        )
        .scalars()
        .all()
    )
