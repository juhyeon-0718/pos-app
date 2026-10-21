"""B-12: 메뉴 소프트 삭제(D-37)와 주문 시 일시품절·삭제 메뉴 거부(409 MENU_UNAVAILABLE)."""
from app.auth import repository as auth_repo
from app.auth.security import hash_password
from app.models.menu import Menu
from app.models.order import Order, OrderItem
from tests.conftest import auth_header, table_session_header
from tests.seed import MENU_A_ID, seed

MENU_B_ID = "m_b12_b"


def _owner(db):
    auth_repo.create_user(db, username="owner_b12", password_hash=hash_password("x"), role="owner")
    return auth_header("owner")


def _menu_b(db, **kw):
    db.add(Menu(id=MENU_B_ID, name="메뉴B", price=8000, category="main", is_active=True, **kw))
    db.commit()


def _order(client, ikey, menu_ids):
    return client.post(
        "/api/v1/orders",
        headers={"Idempotency-Key": ikey, **table_session_header()},
        json={"items": [{"menu_id": m, "qty": 1} for m in menu_ids]},
    )


def _delete(client, db, menu_id):
    return client.delete(f"/api/v1/menus/{menu_id}", headers=_owner(db))


# ── 삭제 ─────────────────────────────────────────────────────

def test_deleted_menu_is_hidden_and_not_editable(client, db):
    seed(db)
    owner = _owner(db)
    assert client.delete(f"/api/v1/menus/{MENU_A_ID}", headers=owner).status_code == 204

    ids = [m["id"] for m in client.get("/api/v1/menus", headers=owner).json()["items"]]
    assert MENU_A_ID not in ids
    ids_guest = [m["id"] for m in client.get("/api/v1/menus", headers=table_session_header()).json()["items"]]
    assert MENU_A_ID not in ids_guest

    r = client.patch(f"/api/v1/menus/{MENU_A_ID}", headers=owner, json={"name": "x", "price": 1})
    assert r.status_code == 404
    assert client.get(f"/api/v1/menus/{MENU_A_ID}/recipe", headers=owner).status_code == 404


def test_delete_menu_twice_returns_404(client, db):
    seed(db)
    owner = _owner(db)
    assert client.delete(f"/api/v1/menus/{MENU_A_ID}", headers=owner).status_code == 204
    assert client.delete(f"/api/v1/menus/{MENU_A_ID}", headers=owner).status_code == 404


def test_delete_requires_owner(client, db):
    seed(db)
    assert client.delete(f"/api/v1/menus/{MENU_A_ID}", headers=auth_header("staff")).status_code == 403


# ── 주문 거부 ────────────────────────────────────────────────

def test_order_with_sold_out_menu_returns_409(client, db):
    seed(db)
    db.get(Menu, MENU_A_ID).is_active = False
    db.commit()
    r = _order(client, "550e8400-e29b-41d4-a716-4466554400c1", [MENU_A_ID])
    assert r.status_code == 409, r.text
    body = r.json()
    assert body["code"] == "MENU_UNAVAILABLE"  # 계약 Error 스키마: 최상위 {code, detail}
    assert isinstance(body["detail"], str) and "메뉴" in body["detail"]


def test_order_with_deleted_menu_returns_409(client, db):
    seed(db)
    assert _delete(client, db, MENU_A_ID).status_code == 204
    r = _order(client, "550e8400-e29b-41d4-a716-4466554400c2", [MENU_A_ID])
    assert r.status_code == 409, r.text
    assert r.json()["code"] == "MENU_UNAVAILABLE"


def test_rejected_order_creates_nothing(client, db):
    """한 메뉴라도 품절이면 정상 메뉴도 주문되지 않고 재고도 차감되지 않는다."""
    seed(db)
    _menu_b(db, )
    db.get(Menu, MENU_B_ID).is_active = False
    db.commit()
    r = _order(client, "550e8400-e29b-41d4-a716-4466554400c3", [MENU_A_ID, MENU_B_ID])
    assert r.status_code == 409
    assert "메뉴B" in r.json()["detail"] and "메뉴A" not in r.json()["detail"]
    db.expire_all()
    assert db.query(Order).count() == 0
    assert db.query(OrderItem).count() == 0


def test_menu_available_again_after_restart_sales(client, db):
    seed(db)
    owner = _owner(db)
    menu = db.get(Menu, MENU_A_ID)
    r = client.patch(f"/api/v1/menus/{MENU_A_ID}", headers=owner,
                     json={"name": menu.name, "price": float(menu.price), "category": menu.category, "is_active": False})
    assert r.status_code == 200
    assert _order(client, "550e8400-e29b-41d4-a716-4466554400c4", [MENU_A_ID]).status_code == 409
    r = client.patch(f"/api/v1/menus/{MENU_A_ID}", headers=owner,
                     json={"name": menu.name, "price": float(menu.price), "category": menu.category, "is_active": True})
    assert r.status_code == 200
    assert _order(client, "550e8400-e29b-41d4-a716-4466554400c5", [MENU_A_ID]).status_code == 201


# ── 과거 주문 ────────────────────────────────────────────────

def test_past_orders_still_readable_after_menu_deleted(client, db):
    seed(db)
    ikey = "550e8400-e29b-41d4-a716-4466554400c6"
    r = _order(client, ikey, [MENU_A_ID])
    assert r.status_code == 201, r.text
    order_id = r.json()["id"]
    assert _delete(client, db, MENU_A_ID).status_code == 204

    mine = client.get("/api/v1/orders/mine", headers=table_session_header())
    assert mine.status_code == 200, mine.text
    found = [o for o in mine.json() if o["id"] == order_id]
    assert found and found[0]["items"][0]["menu_name"] == "메뉴A"

    # 같은 Idempotency-Key 재전송은 메뉴가 삭제된 뒤에도 기존 주문을 그대로 돌려준다.
    again = _order(client, ikey, [MENU_A_ID])
    assert again.status_code == 201 and again.json()["id"] == order_id

    db.expire_all()
    item = db.query(OrderItem).filter(OrderItem.order_id == order_id).one()
    assert item.menu_id == MENU_A_ID  # 소프트 삭제라 참조가 유지된다
