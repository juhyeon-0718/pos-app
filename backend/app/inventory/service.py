"""inventory 모듈 업무 로직. 재고 변경(stock_movements 기록)은 이 모듈을 통해서만 한다 (D-25).

기존 app.services.stock_service(현재 재고 집계, 움직임 기록)를 그대로 쓴다 — B-07에서
이 파일 전체가 app/inventory/ 아래로 합쳐질 때까지 중복 구현하지 않는다.
"""
from sqlalchemy.orm import Session

from app.inventory import repository
from app.models.enums import StockMovementReason
from app.models.ingredient import Ingredient
from app.models.stock_movement import StockMovement
from app.services import stock_service


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


def list_ingredients_with_stock(db: Session) -> list[tuple[Ingredient, float]]:
    ingredients = repository.list_ingredients(db)
    return [(ing, stock_service.current_stock(db, ing.id)) for ing in ingredients]


def get_ingredient_with_stock(db: Session, ingredient_id: str) -> tuple[Ingredient, float]:
    ingredient = repository.get_ingredient(db, ingredient_id)
    if ingredient is None:
        raise NotFound(f"식재료를 찾을 수 없습니다: {ingredient_id}")
    return ingredient, stock_service.current_stock(db, ingredient_id)


def create_ingredient(
    db: Session, *, name: str, unit: str, safety_stock: float, lead_time_days: int, unit_price: float
) -> Ingredient:
    return repository.create_ingredient(
        db, name=name, unit=unit, safety_stock=safety_stock, lead_time_days=lead_time_days, unit_price=unit_price
    )


def update_ingredient(
    db: Session,
    ingredient_id: str,
    *,
    name: str | None,
    unit: str | None,
    safety_stock: float | None,
    lead_time_days: int | None,
    unit_price: float | None,
) -> Ingredient:
    ingredient = repository.get_ingredient(db, ingredient_id)
    if ingredient is None:
        raise NotFound(f"식재료를 찾을 수 없습니다: {ingredient_id}")
    return repository.update_ingredient(
        db,
        ingredient,
        name=name,
        unit=unit,
        safety_stock=safety_stock,
        lead_time_days=lead_time_days,
        unit_price=unit_price,
    )


def deactivate_ingredient(db: Session, ingredient_id: str) -> Ingredient:
    """레시피가 참조 중이면 409 (Conflict)."""
    ingredient = repository.get_ingredient(db, ingredient_id)
    if ingredient is None:
        raise NotFound(f"식재료를 찾을 수 없습니다: {ingredient_id}")
    if repository.recipe_references_ingredient(db, ingredient_id):
        raise Conflict(f"레시피에서 참조 중인 식재료는 비활성화할 수 없습니다: {ingredient_id}")
    return repository.update_ingredient(db, ingredient, is_active=False)


def list_movements(db: Session, ingredient_id: str) -> list[StockMovement]:
    ingredient = repository.get_ingredient(db, ingredient_id)
    if ingredient is None:
        raise NotFound(f"식재료를 찾을 수 없습니다: {ingredient_id}")
    return repository.list_movements(db, ingredient_id)


def create_movement(db: Session, ingredient_id: str, *, qty_delta: float, type_: str, ref_id: str | None) -> StockMovement:
    ingredient = repository.get_ingredient(db, ingredient_id)
    if ingredient is None:
        raise NotFound(f"식재료를 찾을 수 없습니다: {ingredient_id}")
    if not StockMovement.valid_reason(type_):
        raise Conflict(f"알 수 없는 입출고 유형: {type_}")
    movement = stock_service.record_movement(db, ingredient_id, qty_delta, StockMovementReason(type_), ref_id)
    db.commit()
    db.refresh(movement)
    return movement
