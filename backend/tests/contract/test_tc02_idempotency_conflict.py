"""
TC-02: 이미 사용된 Idempotency-Key로 본문이 다른 요청 → 422.

검증 항목:
- 첫 번째 요청은 201 성공
- 같은 키, 다른 본문(qty 변경) → 422
- 응답 detail에 conflict 메시지 포함
- DB: orders 건수 변화 없음, stock_movements 추가 없음

관련 결정: D-15 (Idempotency-Key)
"""
import pytest
from sqlalchemy import func, select

from app.models.order import Order
from app.models.stock_movement import StockMovement
from app.models.enums import StockMovementReason
from tests.conftest import table_session_header
from tests.seed import INGREDIENT_X_ID, MENU_A_ID, seed

IKEY = "550e8400-e29b-41d4-a716-446655440001"


def test_tc02_different_body_same_key_returns_422(client, db):
    """TC-02: 이미 등록된 키로 본문이 다른 요청 → 422."""
    seed(db)

    # 1차 요청 — 키 등록
    r1 = client.post(
        "/api/v1/orders",
        headers={
            "Idempotency-Key": IKEY,
            **table_session_header(),
        },
        json={"items": [{"menu_id": MENU_A_ID, "qty": 1}]},
    )
    assert r1.status_code == 201, f"사전 조건 실패: {r1.text}"

    order_count_before = db.execute(select(func.count()).select_from(Order)).scalar_one()
    movement_count_before = db.execute(
        select(func.count()).select_from(StockMovement).where(
            StockMovement.reason == StockMovementReason.order_deduction.value
        )
    ).scalar_one()

    # 2차 요청 — 같은 키, qty 다름
    r2 = client.post(
        "/api/v1/orders",
        headers={
            "Idempotency-Key": IKEY,
            **table_session_header(),
        },
        json={"items": [{"menu_id": MENU_A_ID, "qty": 99}]},
    )
    assert r2.status_code == 422, f"422 기대, 실제: {r2.status_code} — {r2.text}"

    detail = r2.json().get("detail", {})
    detail_str = str(detail).lower()
    assert "conflict" in detail_str or "mismatch" in detail_str or "idempotency" in detail_str, (
        f"detail에 conflict 메시지 없음: {detail}"
    )

    # DB: orders 건수 변화 없음
    order_count_after = db.execute(select(func.count()).select_from(Order)).scalar_one()
    assert order_count_after == order_count_before, (
        f"orders 건수 변화 있음: {order_count_before} → {order_count_after}"
    )

    # DB: order_deduction 추가 없음
    movement_count_after = db.execute(
        select(func.count()).select_from(StockMovement).where(
            StockMovement.reason == StockMovementReason.order_deduction.value
        )
    ).scalar_one()
    assert movement_count_after == movement_count_before, (
        f"order_deduction 레코드 추가됨: {movement_count_before} → {movement_count_after}"
    )
