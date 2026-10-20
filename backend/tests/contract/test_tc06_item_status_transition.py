"""
TC-06: 항목 상태 변경에 따른 주문 자동 전이.

시나리오 A: 첫 번째 항목 cooking → 주문 cooking 전이 (같은 트랜잭션)
시나리오 B: 모든 항목 done → 주문은 cooking 유지 (served는 직원 수동)

사전 조건:
  - 주문 o_3: received, 항목 2개 (i_1, i_2) 모두 pending
  - 아이템 2개를 위해 메뉴A + 메뉴B 각 1개 주문

관련 결정: D-16
"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient
from app.models.menu import Menu
from app.models.order import Order, OrderItem
from app.models.recipe import RecipeItem
from tests.conftest import table_session_header, auth_header
from tests.seed import INGREDIENT_X_ID, MENU_A_ID, seed

IKEY_06A = "550e8400-e29b-41d4-a716-446655440006"
IKEY_06B = "550e8400-e29b-41d4-a716-446655440007"
MENU_B_ID = "m_seed42_b"


def _seed_menu_b(db: Session) -> None:
    """TC-06 전용 메뉴B (재료X 1개)."""
    db.add(Menu(id=MENU_B_ID, name="메뉴B", price=8000, category="main", is_active=True))
    db.add(RecipeItem(
        menu_id=MENU_B_ID,
        ingredient_id=INGREDIENT_X_ID,
        qty_per_unit=1.0,
        unit="개",
    ))
    db.commit()


def _create_two_item_order(client, ikey: str) -> tuple[str, list[dict]]:
    """메뉴A + 메뉴B 아이템 2개짜리 주문 생성. (order_id, items) 반환."""
    r = client.post(
        "/api/v1/orders",
        headers={"Idempotency-Key": ikey, **table_session_header()},
        json={
            "items": [
                {"menu_id": MENU_A_ID, "qty": 1},
                {"menu_id": MENU_B_ID, "qty": 1},
            ]
        },
    )
    assert r.status_code == 201, f"주문 생성 실패: {r.text}"
    data = r.json()
    return data["id"], data["items"]


# ──────────────────────────────────────────────────────────────
# TC-06 시나리오 A
# ──────────────────────────────────────────────────────────────

def test_tc06a_first_item_cooking_transitions_order_to_cooking(client, db):
    """TC-06A: 첫 번째 항목 cooking → 주문 cooking 전이, 두 번째 항목은 pending 유지."""
    seed(db)
    _seed_menu_b(db)

    order_id, items = _create_two_item_order(client, IKEY_06A)
    assert len(items) == 2, f"아이템 수: {len(items)} (기대 2)"

    # 첫 번째 아이템 cooking
    r = client.patch(
        f"/api/v1/kitchen/items/{items[0]['id']}/status",
        headers=auth_header("kitchen"), json={"status": "cooking"},
    )
    assert r.status_code == 200, f"아이템 상태 변경 실패: {r.text}"
    assert r.json()["status"] == "cooking"

    # DB: 주문 cooking 전이
    order = db.get(Order, order_id)
    db.refresh(order)
    assert order.status == "cooking", (
        f"주문 상태: {order.status} (기대 cooking)"
    )

    # DB: 두 번째 아이템은 pending 유지
    second_item = db.get(OrderItem, items[1]["id"])
    assert second_item.item_status == "pending", (
        f"두 번째 아이템 상태: {second_item.item_status} (기대 pending)"
    )


# ──────────────────────────────────────────────────────────────
# TC-06 시나리오 B
# ──────────────────────────────────────────────────────────────

def test_tc06b_all_items_done_order_stays_cooking(client, db):
    """TC-06B: 모든 항목 done → 주문 cooking 유지 (served 자동 전이 없음)."""
    seed(db)
    _seed_menu_b(db)

    order_id, items = _create_two_item_order(client, IKEY_06B)

    # 모든 아이템 cooking → done
    for item in items:
        r = client.patch(
            f"/api/v1/kitchen/items/{item['id']}/status",
            headers=auth_header("kitchen"), json={"status": "cooking"},
        )
        assert r.status_code == 200
        r = client.patch(
            f"/api/v1/kitchen/items/{item['id']}/status",
            headers=auth_header("kitchen"), json={"status": "done"},
        )
        assert r.status_code == 200

    # DB: 주문 cooking 유지 (served로 자동 전이 금지)
    order = db.get(Order, order_id)
    db.refresh(order)
    assert order.status == "cooking", (
        f"주문 상태: {order.status} (기대 cooking — served는 직원 수동, D-16)"
    )

    # DB: 두 아이템 모두 done
    for item in items:
        oi = db.get(OrderItem, item["id"])
        assert oi.item_status == "done", (
            f"아이템 {oi.id} 상태: {oi.item_status} (기대 done)"
        )
