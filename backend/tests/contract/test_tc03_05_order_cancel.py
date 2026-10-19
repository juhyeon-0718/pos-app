"""
TC-03~TC-05: 주문 취소 시나리오 (조리 전/후, 권한).

TC-03: 조리 전 취소 → 재고 복원 (cancel_restore), disposal 없음
TC-04: 조리 후 취소 → cancel_restore + disposal 한 쌍, 재고 유지
TC-05: 직원이 조리 후 취소 시도 → 403, 주문 상태 유지

관련 결정: D-06, D-16, D-19
"""
import pytest
from sqlalchemy import func, select

from app.models.enums import StockMovementReason
from app.models.order import Order
from app.models.stock_movement import StockMovement
from tests.conftest import auth_header, table_session_header
from tests.seed import (
    INGREDIENT_X_ID,
    INGREDIENT_X_INITIAL_STOCK,
    MENU_A_ID,
    RECIPE_QTY_PER_UNIT,
    seed,
)

IKEY_03 = "550e8400-e29b-41d4-a716-446655440003"
IKEY_04 = "550e8400-e29b-41d4-a716-446655440004"
IKEY_05 = "550e8400-e29b-41d4-a716-446655440005"


def _create_order(client, ikey: str) -> tuple[str, str]:
    """주문 생성 후 (order_id, first_item_id) 반환."""
    r = client.post(
        "/api/v1/orders",
        headers={"Idempotency-Key": ikey, **table_session_header()},
        json={"items": [{"menu_id": MENU_A_ID, "qty": 1}]},
    )
    assert r.status_code == 201, f"주문 생성 실패: {r.text}"
    data = r.json()
    return data["id"], data["items"][0]["id"]


def _set_item_cooking(client, item_id: str) -> None:
    """kitchen 엔드포인트로 아이템 상태를 cooking으로 변경."""
    r = client.patch(
        f"/api/v1/kitchen/items/{item_id}/status",
        json={"status": "cooking"},
    )
    assert r.status_code == 200, f"아이템 상태 변경 실패: {r.text}"


def _stock_sum(db, ingredient_id: str) -> float:
    return float(
        db.execute(
            select(func.coalesce(func.sum(StockMovement.qty_delta), 0)).where(
                StockMovement.ingredient_id == ingredient_id
            )
        ).scalar_one()
    )


# ──────────────────────────────────────────────────────────────
# TC-03
# ──────────────────────────────────────────────────────────────

def test_tc03_cancel_before_cooking_restores_stock(client, db):
    """TC-03: received 상태 주문 취소 → cancel_restore, disposal 없음, 재고 복원."""
    seed(db)
    order_id, _ = _create_order(client, IKEY_03)

    r_cancel = client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers=auth_header("staff"),
        json={"status": "cancelled"},
    )
    assert r_cancel.status_code == 200, f"취소 실패: {r_cancel.text}"
    assert r_cancel.json()["status"] == "cancelled"

    # cancel_restore 1건
    restore = db.execute(
        select(func.count()).select_from(StockMovement).where(
            StockMovement.ingredient_id == INGREDIENT_X_ID,
            StockMovement.reason == StockMovementReason.cancel_restore.value,
        )
    ).scalar_one()
    assert restore == 1, f"cancel_restore: {restore}건 (기대 1)"

    # disposal 0건
    disposal = db.execute(
        select(func.count()).select_from(StockMovement).where(
            StockMovement.ingredient_id == INGREDIENT_X_ID,
            StockMovement.reason == StockMovementReason.disposal.value,
        )
    ).scalar_one()
    assert disposal == 0, f"disposal: {disposal}건 (조리 전 취소 시 없어야 함)"

    # 재고 10 복원
    assert _stock_sum(db, INGREDIENT_X_ID) == pytest.approx(INGREDIENT_X_INITIAL_STOCK), (
        f"재고 복원 실패: {_stock_sum(db, INGREDIENT_X_ID)} (기대 {INGREDIENT_X_INITIAL_STOCK})"
    )


# ──────────────────────────────────────────────────────────────
# TC-04
# ──────────────────────────────────────────────────────────────

def test_tc04_cancel_after_cooking_records_disposal(client, db):
    """TC-04: cooking 상태 주문 취소(owner) → cancel_restore + disposal 한 쌍, 재고 8 유지."""
    seed(db)
    order_id, item_id = _create_order(client, IKEY_04)
    _set_item_cooking(client, item_id)

    r_cancel = client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers=auth_header("owner"),
        json={"status": "cancelled"},
    )
    assert r_cancel.status_code == 200, f"취소 실패: {r_cancel.text}"
    assert r_cancel.json()["status"] == "cancelled"

    # cancel_restore 1건
    restore = db.execute(
        select(func.count()).select_from(StockMovement).where(
            StockMovement.ingredient_id == INGREDIENT_X_ID,
            StockMovement.reason == StockMovementReason.cancel_restore.value,
        )
    ).scalar_one()
    assert restore == 1, f"cancel_restore: {restore}건 (기대 1)"

    # disposal 1건
    disposal = db.execute(
        select(func.count()).select_from(StockMovement).where(
            StockMovement.ingredient_id == INGREDIENT_X_ID,
            StockMovement.reason == StockMovementReason.disposal.value,
        )
    ).scalar_one()
    assert disposal == 1, f"disposal: {disposal}건 (기대 1)"

    # 재고 8 유지 (cancel_restore +2, disposal -2 → 순 변화 0)
    expected = INGREDIENT_X_INITIAL_STOCK - RECIPE_QTY_PER_UNIT  # 8.0
    assert _stock_sum(db, INGREDIENT_X_ID) == pytest.approx(expected), (
        f"재고: {_stock_sum(db, INGREDIENT_X_ID)} (기대 {expected})"
    )


# ──────────────────────────────────────────────────────────────
# TC-05
# ──────────────────────────────────────────────────────────────

def test_tc05_staff_cannot_cancel_after_cooking(client, db):
    """TC-05: 직원이 cooking 주문 취소 시도 → 403, 주문 cooking 유지."""
    seed(db)
    order_id, item_id = _create_order(client, IKEY_05)
    _set_item_cooking(client, item_id)

    r_cancel = client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers=auth_header("staff"),
        json={"status": "cancelled"},
    )
    assert r_cancel.status_code == 403, (
        f"403 기대, 실제: {r_cancel.status_code} — {r_cancel.text}"
    )
    assert "사장" in r_cancel.json().get("detail", ""), (
        f"detail에 '사장' 메시지 없음: {r_cancel.json()}"
    )

    # DB: 주문 상태 cooking 유지
    order = db.get(Order, order_id)
    db.refresh(order)
    assert order.status == "cooking", f"주문 상태 변경됨: {order.status}"

    # DB: cancel_restore, disposal 없음
    extra = db.execute(
        select(func.count()).select_from(StockMovement).where(
            StockMovement.ingredient_id == INGREDIENT_X_ID,
            StockMovement.reason.in_([
                StockMovementReason.cancel_restore.value,
                StockMovementReason.disposal.value,
            ]),
        )
    ).scalar_one()
    assert extra == 0, f"cancel_restore/disposal 레코드 추가됨: {extra}건"
