"""
B-07: 서빙완료 전이 조건 (D-32).
모든 항목 done(취소 항목 제외)일 때만 served 허용, 아니면 409.
"""
from app.models.order import OrderItem
from tests.conftest import auth_header, table_session_header
from tests.seed import MENU_A_ID, seed
from tests.contract.test_tc06_item_status_transition import MENU_B_ID, _create_two_item_order, _seed_menu_b


def _serve(client, order_id):
    return client.patch(
        f"/api/v1/orders/{order_id}/status",
        headers=auth_header("staff"),
        json={"status": "served"},
    )


def _set_item(client, item_id, status):
    r = client.patch(f"/api/v1/kitchen/items/{item_id}/status", json={"status": status})
    assert r.status_code == 200, r.text


def test_b07_all_done_serves(client, db):
    seed(db)
    _seed_menu_b(db)
    order_id, items = _create_two_item_order(client, "550e8400-e29b-41d4-a716-4466554400b1")
    for it in items:
        _set_item(client, it["id"], "done")
    r = _serve(client, order_id)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "served"


def test_b07_partial_cooking_returns_409(client, db):
    seed(db)
    _seed_menu_b(db)
    order_id, items = _create_two_item_order(client, "550e8400-e29b-41d4-a716-4466554400b2")
    _set_item(client, items[0]["id"], "done")
    _set_item(client, items[1]["id"], "cooking")
    r = _serve(client, order_id)
    assert r.status_code == 409, r.text
    assert "detail" in r.json() or "message" in r.json() or "error" in r.json()
    check = client.get("/api/v1/orders/mine", headers=table_session_header()).json()
    assert [o for o in check if o["id"] == order_id][0]["status"] == "cooking"


def test_b07_cancelled_item_excluded(client, db):
    seed(db)
    _seed_menu_b(db)
    order_id, items = _create_two_item_order(client, "550e8400-e29b-41d4-a716-4466554400b3")
    _set_item(client, items[0]["id"], "done")
    cancelled = db.get(OrderItem, items[1]["id"])
    cancelled.item_status = "cancelled"
    db.commit()
    r = _serve(client, order_id)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "served"
