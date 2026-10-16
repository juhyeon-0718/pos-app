"""
재고(stock_movements) 관련 서비스. D-05: 원장 합계 = 현재 재고.
직접 UPDATE로 재고를 고치지 않고, 움직임(qty_delta)만 쌓은 뒤 잔량은 집계로 구한다.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import StockMovementReason
from app.models.ingredient import Ingredient
from app.models.stock_movement import StockMovement


def current_stock(db: Session, ingredient_id: str) -> float:
    total = db.execute(
        select(func.coalesce(func.sum(StockMovement.qty_delta), 0)).where(
            StockMovement.ingredient_id == ingredient_id
        )
    ).scalar_one()
    return float(total)


def lock_ingredient_for_update(db: Session, ingredient_id: str) -> None:
    """
    동시 주문 접수 시 같은 식재료의 재고 차감이 레이스 없이 순서대로 쌓이도록
    ingredients 행을 SELECT ... FOR UPDATE로 잠근다 (PostgreSQL 전용, D-21).
    stock_movements는 원장이라 잠글 "현재 재고" 행이 없으므로 대신 상위 ingredients
    행을 잠가 critical section을 만든다. 호출자는 같은 트랜잭션 안에서
    current_stock 조회 전에 이 함수를 먼저 호출해야 한다.
    """
    db.execute(select(Ingredient.id).where(Ingredient.id == ingredient_id).with_for_update())


def record_movement(
    db: Session,
    ingredient_id: str,
    qty_delta: float,
    reason: StockMovementReason,
    ref_id: str | None = None,
) -> StockMovement:
    movement = StockMovement(
        ingredient_id=ingredient_id,
        qty_delta=qty_delta,
        reason=reason.value,
        ref_id=ref_id,
    )
    db.add(movement)
    return movement
