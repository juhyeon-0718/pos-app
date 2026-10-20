"""B-06: 메뉴·식재료 CRUD, 레시피, 입출고(movements).

완료 조건: 재고 변경은 inventory service로만 함, 레시피 참조 중인 식재료
비활성화는 409.
"""
from app.auth import repository as auth_repo
from app.auth.security import hash_password
from app.models.ingredient import Ingredient
from app.models.menu import Menu
from app.models.recipe import RecipeItem
from tests.conftest import auth_header


def _owner_header(db):
    auth_repo.create_user(db, username="owner_b06", password_hash=hash_password("x"), role="owner")
    return auth_header("owner")


# ──────────────────────────────────────────────────────────────
# 메뉴 CRUD
# ──────────────────────────────────────────────────────────────


def test_create_menu_owner(client, db):
    r = client.post(
        "/api/v1/menus",
        headers=_owner_header(db),
        json={"name": "비빔밥", "price": 9000, "category": "main", "is_active": True},
    )
    assert r.status_code == 201, r.text
    assert r.json()["name"] == "비빔밥"


def test_create_menu_requires_owner(client, db):
    r = client.post(
        "/api/v1/menus",
        headers=auth_header("staff"),
        json={"name": "비빔밥", "price": 9000},
    )
    assert r.status_code == 403, r.text


def test_update_menu_not_found(client, db):
    r = client.patch(
        "/api/v1/menus/nope",
        headers=_owner_header(db),
        json={"name": "x", "price": 1},
    )
    assert r.status_code == 404, r.text


def test_deactivate_menu_sets_is_active_false(client, db):
    menu = Menu(name="돈까스", price=8000, category="main", is_active=True)
    db.add(menu)
    db.commit()
    db.refresh(menu)

    r = client.delete(f"/api/v1/menus/{menu.id}", headers=_owner_header(db))
    assert r.status_code == 204, r.text

    db.refresh(menu)
    assert menu.is_active is False


def test_list_menus_requires_some_auth(client, db):
    r = client.get("/api/v1/menus")
    assert r.status_code == 401, r.text


def test_list_menus_with_table_token(client, db):
    from tests.conftest import table_session_header
    from tests.seed import seed

    seed(db)
    r = client.get("/api/v1/menus", headers=table_session_header())
    assert r.status_code == 200, r.text
    body = r.json()
    # 계약 MenuListResponse: 최상위가 배열이 아니라 {items, next_cursor, has_more}
    assert isinstance(body, dict)
    assert body["has_more"] is False and body["next_cursor"] is None
    assert len(body["items"]) >= 1


# ──────────────────────────────────────────────────────────────
# 레시피
# ──────────────────────────────────────────────────────────────


def test_put_and_get_menu_recipe(client, db):
    menu = Menu(name="김치찌개", price=7000, category="main", is_active=True)
    ingredient = Ingredient(name="김치", unit="g", safety_stock=0, lead_time_days=1, unit_price=10)
    db.add_all([menu, ingredient])
    db.commit()
    db.refresh(menu)
    db.refresh(ingredient)

    owner = _owner_header(db)
    r = client.put(
        f"/api/v1/menus/{menu.id}/recipe",
        headers=owner,
        json=[{"ingredient_id": ingredient.id, "qty_per_unit": 200, "unit": "g"}],
    )
    assert r.status_code == 200, r.text
    assert len(r.json()) == 1

    r2 = client.get(f"/api/v1/menus/{menu.id}/recipe", headers=auth_header("staff"))
    assert r2.status_code == 200, r2.text
    assert r2.json()[0]["ingredient_id"] == ingredient.id


# ──────────────────────────────────────────────────────────────
# 식재료 CRUD
# ──────────────────────────────────────────────────────────────


def test_create_ingredient_and_list_shows_zero_stock(client, db):
    owner = _owner_header(db)
    r = client.post(
        "/api/v1/ingredients",
        headers=owner,
        json={"name": "양파", "unit": "개", "safety_stock": 5, "lead_time_days": 2, "unit_price": 500},
    )
    assert r.status_code == 201, r.text
    assert r.json()["current_stock"] == 0.0

    r2 = client.get("/api/v1/ingredients", headers=owner)
    assert r2.status_code == 200, r2.text
    assert set(r2.json()) >= {"items", "next_cursor", "has_more"}
    assert r2.json()["has_more"] is False
    names = [i["name"] for i in r2.json()["items"]]
    assert "양파" in names


def test_deactivate_ingredient_referenced_by_recipe_returns_409(client, db):
    menu = Menu(name="파스타", price=12000, category="main", is_active=True)
    ingredient = Ingredient(name="면", unit="g", safety_stock=0, lead_time_days=1, unit_price=5)
    db.add_all([menu, ingredient])
    db.commit()
    db.refresh(menu)
    db.refresh(ingredient)
    db.add(RecipeItem(menu_id=menu.id, ingredient_id=ingredient.id, qty_per_unit=100, unit="g"))
    db.commit()

    owner = _owner_header(db)
    r = client.delete(f"/api/v1/ingredients/{ingredient.id}", headers=owner)
    assert r.status_code == 409, r.text


def test_deactivate_ingredient_without_recipe_succeeds(client, db):
    ingredient = Ingredient(name="소금", unit="g", safety_stock=0, lead_time_days=1, unit_price=1)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    owner = _owner_header(db)
    r = client.delete(f"/api/v1/ingredients/{ingredient.id}", headers=owner)
    assert r.status_code == 200, r.text
    assert r.json()["is_active"] is False


# ──────────────────────────────────────────────────────────────
# 입출고(movements) — inventory service로만 재고가 바뀌는지
# ──────────────────────────────────────────────────────────────


def test_create_movement_updates_current_stock(client, db):
    ingredient = Ingredient(name="설탕", unit="g", safety_stock=0, lead_time_days=1, unit_price=2)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    owner = _owner_header(db)
    r = client.post(
        f"/api/v1/ingredients/{ingredient.id}/movements",
        headers=owner,
        json={"qty_delta": 50, "type": "restock"},
    )
    assert r.status_code == 201, r.text

    r2 = client.get("/api/v1/ingredients", headers=owner)
    body = next(i for i in r2.json()["items"] if i["id"] == ingredient.id)
    assert body["current_stock"] == 50.0

    r3 = client.get(f"/api/v1/ingredients/{ingredient.id}/movements", headers=owner)
    assert r3.status_code == 200, r3.text
    assert set(r3.json()) >= {"items", "next_cursor", "has_more"}
    assert len(r3.json()["items"]) == 1
    assert r3.json()["items"][0]["type"] == "restock"


def test_create_movement_invalid_type_returns_422(client, db):
    ingredient = Ingredient(name="후추", unit="g", safety_stock=0, lead_time_days=1, unit_price=3)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    owner = _owner_header(db)
    r = client.post(
        f"/api/v1/ingredients/{ingredient.id}/movements",
        headers=owner,
        json={"qty_delta": 10, "type": "not_a_real_type"},
    )
    assert r.status_code == 422, r.text
