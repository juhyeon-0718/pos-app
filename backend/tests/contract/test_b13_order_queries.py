"""B-13: 주문 조회 API(GET /orders, /orders/{id}, /kitchen/queue)와 계약 경로 구현 점검."""
import re
from pathlib import Path

from app.main import app
from tests.conftest import auth_header, table_session_header
from tests.contract.test_tc06_item_status_transition import MENU_B_ID, _seed_menu_b
from tests.seed import MENU_A_ID, TABLE_TEST_ID, seed

_SPEC = Path(__file__).resolve().parents[3] / "docs" / "api" / "openapi.yaml"
# 파일럿(1차) 범위 밖이라 아직 구현하지 않는 경로. 새 경로를 여기에 몰래 추가하지 않는다(D-30, 민준 승인 필요).
_PHASE2_PATHS = {
    "/stream/orders",  # SSE는 5초 폴링으로 대체(D-30)
    "/purchase-recommendations",
    "/purchase-recommendations/cooldown-settings",
    "/purchase-recommendations/{}/approve",
    "/purchase-recommendations/{}/reject",
    "/analytics/sales",
    "/analytics/sales/summary",
    "/analytics/ingredient-usage",
}


def _contract_routes() -> set[tuple[str, str]]:
    text = _SPEC.read_text(encoding="utf-8")
    block = text.split("\npaths:", 1)[1].split("\ncomponents:", 1)[0]
    cur, found = None, set()
    for line in block.splitlines():
        m = re.match(r"^  (/[^:\s]*):\s*$", line)
        if m:
            cur = re.sub(r"\{[^}]*\}", "{}", m.group(1))
            continue
        m = re.match(r"^    (get|post|put|patch|delete):", line)
        if m and cur:
            found.add((m.group(1).upper(), cur))
    return found


def test_every_contract_route_is_implemented_except_phase2():
    """openapi의 모든 경로·메서드가 FastAPI 라우트에 있어야 한다(목킹 테스트가 못 잡는 누락 방지)."""
    implemented = {
        (m, re.sub(r"\{[^}]*\}", "{}", r.path.removeprefix("/api/v1")))
        for r in app.routes
        if hasattr(r, "methods")
        for m in r.methods
        if m not in ("HEAD", "OPTIONS")
    }
    missing = {(m, p) for (m, p) in _contract_routes() - implemented if p not in _PHASE2_PATHS}
    assert not missing, f"계약에 있는데 구현되지 않은 경로: {sorted(missing)}"


def _create_order(client, ikey, menu_ids=(MENU_A_ID,)):
    r = client.post(
        "/api/v1/orders",
        headers={"Idempotency-Key": ikey, **table_session_header()},
        json={"items": [{"menu_id": m, "qty": 1} for m in menu_ids]},
    )
    assert r.status_code == 201, r.text
    return r.json()


# ── GET /orders ──────────────────────────────────────────────

def test_list_orders_has_wrapper_and_table_no(client, db):
    seed(db)
    created = _create_order(client, "550e8400-e29b-41d4-a716-4466554400d1")
    assert created["table_no"] == 1  # POST /orders 응답에도 table_no

    r = client.get("/api/v1/orders", headers=auth_header("staff"))
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body) >= {"items", "next_cursor", "has_more"}
    assert body["next_cursor"] is None and body["has_more"] is False
    assert [o["id"] for o in body["items"]] == [created["id"]]
    order = body["items"][0]
    assert order["table_no"] == 1 and order["table_id"] == TABLE_TEST_ID
    assert order["items"][0]["table_no"] == 1


def test_list_orders_status_filter_and_contract_params(client, db):
    seed(db)
    a = _create_order(client, "550e8400-e29b-41d4-a716-4466554400d2")
    b = _create_order(client, "550e8400-e29b-41d4-a716-4466554400d3")
    staff = auth_header("staff")
    assert client.patch(f"/api/v1/orders/{a['id']}/status", headers=staff, json={"status": "cooking"}).status_code == 200

    only_cooking = client.get("/api/v1/orders?status=cooking", headers=staff).json()["items"]
    assert [o["id"] for o in only_cooking] == [a["id"]]
    received = client.get("/api/v1/orders?status=received&limit=50", headers=staff).json()["items"]
    assert [o["id"] for o in received] == [b["id"]]
    assert client.get("/api/v1/orders?status=nope", headers=staff).status_code == 422
    assert client.get("/api/v1/orders?from=2999-01-01T00:00:00Z", headers=staff).json()["items"] == []
    assert len(client.get("/api/v1/orders?to=2999-01-01T00:00:00Z", headers=staff).json()["items"]) == 2


def test_list_orders_requires_bearer(client, db):
    seed(db)
    assert client.get("/api/v1/orders").status_code == 401
    # 손님 테이블 토큰은 전체 주문 목록을 볼 수 없다.
    assert client.get("/api/v1/orders", headers=table_session_header()).status_code == 401


# ── GET /orders/{id} ─────────────────────────────────────────

def test_get_order_by_staff_and_by_own_table(client, db):
    seed(db)
    created = _create_order(client, "550e8400-e29b-41d4-a716-4466554400d4")
    url = f"/api/v1/orders/{created['id']}"
    r = client.get(url, headers=auth_header("kitchen"))
    assert r.status_code == 200 and r.json()["id"] == created["id"] and r.json()["table_no"] == 1
    r = client.get(url, headers=table_session_header())
    assert r.status_code == 200 and r.json()["id"] == created["id"]


def test_get_order_404_and_other_table_hidden(client, db):
    from app.auth import repository as auth_repo

    seed(db)
    created = _create_order(client, "550e8400-e29b-41d4-a716-4466554400d5")
    other = auth_repo.create_table(db, table_no=2)
    from app.auth.security import create_table_session_token

    other_hdr = {"X-Table-Session-Token": create_table_session_token(table_id=other.id, qr_token=other.qr_token)}
    assert client.get(f"/api/v1/orders/{created['id']}", headers=other_hdr).status_code == 404
    assert client.get("/api/v1/orders/nope", headers=auth_header("staff")).status_code == 404
    assert client.get(f"/api/v1/orders/{created['id']}").status_code == 401


# ── GET /kitchen/queue ───────────────────────────────────────

def test_kitchen_queue_is_plain_array_with_table_no(client, db):
    seed(db)
    _seed_menu_b(db)
    o = _create_order(client, "550e8400-e29b-41d4-a716-4466554400d6", (MENU_A_ID, MENU_B_ID))
    kitchen = auth_header("kitchen")

    r = client.get("/api/v1/kitchen/queue", headers=kitchen)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)  # 계약: 래퍼 없는 OrderItem[]
    assert {i["id"] for i in body} == {i["id"] for i in o["items"]}
    assert all(i["table_no"] == 1 and i["item_status"] == "pending" for i in body)

    # done이 된 항목은 큐에서 빠진다.
    first = body[0]["id"]
    assert client.patch(f"/api/v1/kitchen/items/{first}/status", headers=kitchen, json={"status": "done"}).status_code == 200
    ids = {i["id"] for i in client.get("/api/v1/kitchen/queue", headers=kitchen).json()}
    assert first not in ids and len(ids) == 1


def test_kitchen_queue_excludes_cancelled_orders(client, db):
    seed(db)
    o = _create_order(client, "550e8400-e29b-41d4-a716-4466554400d7")
    r = client.patch(f"/api/v1/orders/{o['id']}/status", headers=auth_header("staff"), json={"status": "cancelled"})
    assert r.status_code == 200, r.text
    assert client.get("/api/v1/kitchen/queue", headers=auth_header("kitchen")).json() == []


def test_kitchen_endpoints_require_login(client, db):
    seed(db)
    assert client.get("/api/v1/kitchen/queue").status_code == 401
    assert client.patch("/api/v1/kitchen/items/x/status", json={"status": "done"}).status_code == 401
