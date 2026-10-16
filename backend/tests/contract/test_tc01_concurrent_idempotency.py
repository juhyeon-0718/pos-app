"""
TC-01: 같은 Idempotency-Key로 동시에 2건 요청 → 주문 1건, 재고 차감 1회.

검증 항목:
- 두 응답 모두 HTTP 201
- 두 응답의 order id가 동일 (같은 주문 반환)
- DB: orders 1건, stock_movements(order_deduction) 1건
- DB: 현재고 = 초기(10) - 1회차감(2) = 8
- DB: idempotency_keys 1건
- 응답: stock_warnings 빈 배열 (재고 충분)

관련 결정: D-15 (Idempotency-Key), D-21 (PostgreSQL)
실행 전제: PostgreSQL 설치 완료, DATABASE_URL 설정 (D-21)
"""
import threading

import pytest
from sqlalchemy import func, select

from tests.seed import (
    INGREDIENT_X_ID,
    INGREDIENT_X_INITIAL_STOCK,
    MENU_A_ID,
    RECIPE_QTY_PER_UNIT,
    seed,
)

IKEY = "550e8400-e29b-41d4-a716-446655440001"


def test_tc01_concurrent_same_key_creates_one_order(client, db):
    """TC-01: 같은 키로 동시 2건 → orders 1건, stock_movements(order_deduction) 1건."""
    seed(db)

    results: list = [None, None]
    exceptions: list = [None, None]
    barrier = threading.Barrier(2, timeout=5)

    def worker(idx: int) -> None:
        try:
            barrier.wait()  # 두 스레드가 최대한 동시에 요청하도록 동기화
            resp = client.post(
                "/api/v1/orders",
                headers={
                    "Idempotency-Key": IKEY,
                    "X-Table-Session-Token": "t_test",
                },
                json={"items": [{"menu_id": MENU_A_ID, "qty": 1}]},
            )
            results[idx] = resp
        except Exception as exc:  # noqa: BLE001
            exceptions[idx] = exc

    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)

    # 스레드 내 예외 전파
    for exc in exceptions:
        if exc is not None:
            raise exc

    assert results[0] is not None, "worker 0이 응답을 받지 못했습니다"
    assert results[1] is not None, "worker 1이 응답을 받지 못했습니다"

    # ── 응답 검증 ──────────────────────────────────────────
    r0, r1 = results
    assert r0.status_code == 201, f"요청0 상태코드: {r0.status_code} — {r0.text}"
    assert r1.status_code == 201, f"요청1 상태코드: {r1.status_code} — {r1.text}"

    id0 = r0.json()["id"]
    id1 = r1.json()["id"]
    assert id0 == id1, f"order id 불일치: {id0} != {id1} (중복 주문 생성됨)"

    assert r0.json().get("stock_warnings", []) == [], "stock_warnings는 빈 배열이어야 합니다"
    assert r1.json().get("stock_warnings", []) == [], "stock_warnings는 빈 배열이어야 합니다"

    # ── DB 검증 ────────────────────────────────────────────
    # worker 커밋 이후 db 세션으로 직접 조회 (READ COMMITTED — 커밋된 데이터 읽힘)
    from app.models.idempotency_key import IdempotencyKey
    from app.models.order import Order
    from app.models.stock_movement import StockMovement
    from app.models.enums import StockMovementReason

    order_count = db.execute(
        select(func.count()).select_from(Order)
    ).scalar_one()
    assert order_count == 1, f"orders 레코드: {order_count}건 (기대 1건, 중복 생성 의심)"

    deduction_count = db.execute(
        select(func.count()).select_from(StockMovement).where(
            StockMovement.reason == StockMovementReason.order_deduction.value,
            StockMovement.ingredient_id == INGREDIENT_X_ID,
        )
    ).scalar_one()
    assert deduction_count == 1, (
        f"order_deduction 레코드: {deduction_count}건 (기대 1건, 이중 재고 차감 의심)"
    )

    actual_stock = float(
        db.execute(
            select(func.coalesce(func.sum(StockMovement.qty_delta), 0)).where(
                StockMovement.ingredient_id == INGREDIENT_X_ID
            )
        ).scalar_one()
    )
    expected_stock = INGREDIENT_X_INITIAL_STOCK - RECIPE_QTY_PER_UNIT  # 10 - 2 = 8
    assert actual_stock == pytest.approx(expected_stock), (
        f"현재고: {actual_stock} (기대 {expected_stock})"
    )

    ikey_count = db.execute(
        select(func.count()).select_from(IdempotencyKey)
    ).scalar_one()
    assert ikey_count == 1, f"idempotency_keys 레코드: {ikey_count}건 (기대 1건)"
