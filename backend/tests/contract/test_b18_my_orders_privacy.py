"""
B-18: GET /orders/mine에서 앞 손님의 주문이 보이지 않는다.

- 결제 완료(paid) 주문은 응답에서 뺀다.
- 취소 주문은 세션 토큰 발급(iat) 이후에 만들어진 것만 돌려준다.
- 결제해도 세션 토큰은 만료되지 않는다(401 아님).
"""
from datetime import datetime, timedelta, timezone

from app.models.order import Order
from tests.conftest import auth_header, table_session_header
from tests.seed import MENU_A_ID, seed


def _create_order(client, ikey: str) -> str:
    r = client.post(
        "/api/v1/orders",
        headers={"Idempotency-Key": ikey, **table_session_header()},
        json={"items": [{"menu_id": MENU_A_ID, "qty": 1}]},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _mine(client) -> list[dict]:
    r = client.get("/api/v1/orders/mine", headers=table_session_header())
    assert r.status_code == 200, r.text
    return r.json()


def test_b18_paid_order_hidden_from_new_session(client, db):
    seed(db)
    order_id = _create_order(client, "550e8400-e29b-41d4-a716-4466554418a1")
    assert [o["id"] for o in _mine(client)] == [order_id]

    order = db.get(Order, order_id)
    order.status = "paid"  # 직원 결제 처리 이후 상태
    db.commit()

    # 같은 테이블에서 새로 스캔한 손님(새 토큰)에게는 이전 주문이 0건이다.
    assert _mine(client) == []


def test_b18_cancelled_filtered_by_session_iat(client, db):
    seed(db)
    old_id = _create_order(client, "550e8400-e29b-41d4-a716-4466554418b1")
    new_id = _create_order(client, "550e8400-e29b-41d4-a716-4466554418b2")
    for oid in (old_id, new_id):
        r = client.patch(
            f"/api/v1/orders/{oid}/status", headers=auth_header("staff"), json={"status": "cancelled"}
        )
        assert r.status_code == 200, r.text

    # 앞 손님의 취소 주문: 토큰 발급 1시간 전에 만들어진 것으로 되돌린다.
    db.get(Order, old_id).created_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db.commit()

    ids = [o["id"] for o in _mine(client)]
    assert ids == [new_id]
    assert old_id not in ids


def test_b18_session_not_expired_after_payment(client, db):
    seed(db)
    order_id = _create_order(client, "550e8400-e29b-41d4-a716-4466554418c1")
    db.get(Order, order_id).status = "paid"
    db.commit()
    # 결제 후에도 같은 토큰으로 다시 주문할 수 있다(세션 만료 안 함).
    assert _create_order(client, "550e8400-e29b-41d4-a716-4466554418c2")
    assert len(_mine(client)) == 1
