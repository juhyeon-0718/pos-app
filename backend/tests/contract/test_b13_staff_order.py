"""B-13: 직원 대리 주문(bearer + table_id). 계약 createOrder의 StaffOrderRequest."""
from app.auth import repository as auth_repo
from tests.conftest import auth_header, table_session_header
from tests.seed import MENU_A_ID, TABLE_TEST_ID, seed

ITEMS = [{"menu_id": MENU_A_ID, "qty": 1}]


def _post(client, ikey, headers, **body):
    return client.post("/api/v1/orders", headers={"Idempotency-Key": ikey, **headers}, json={"items": ITEMS, **body})


def test_staff_can_order_for_a_table(client, db):
    seed(db)
    r = _post(client, "550e8400-e29b-41d4-a716-4466554400e1", auth_header("staff"), table_id=TABLE_TEST_ID)
    assert r.status_code == 201, r.text
    assert r.json()["table_id"] == TABLE_TEST_ID and r.json()["table_no"] == 1


def test_staff_order_needs_table_id_and_existing_table(client, db):
    seed(db)
    assert _post(client, "550e8400-e29b-41d4-a716-4466554400e2", auth_header("staff")).status_code == 422
    assert _post(client, "550e8400-e29b-41d4-a716-4466554400e3", auth_header("owner"), table_id="nope").status_code == 404


def test_kitchen_cannot_create_orders(client, db):
    seed(db)
    r = _post(client, "550e8400-e29b-41d4-a716-4466554400e4", auth_header("kitchen"), table_id=TABLE_TEST_ID)
    assert r.status_code == 403


def test_customer_cannot_choose_another_table(client, db):
    seed(db)
    other = auth_repo.create_table(db, table_no=2)
    assert _post(client, "550e8400-e29b-41d4-a716-4466554400e5", table_session_header(), table_id=other.id).status_code == 422
    assert _post(client, "550e8400-e29b-41d4-a716-4466554400e6", table_session_header()).status_code == 201


def test_order_requires_some_auth(client, db):
    seed(db)
    assert _post(client, "550e8400-e29b-41d4-a716-4466554400e7", {}).status_code == 401
