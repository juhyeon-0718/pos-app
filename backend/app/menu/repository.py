"""menu 모듈 DB 접근 계층. menus/recipes 테이블만 다룬다 (D-25).

식재료 모델(app.models.ingredient)은 참조만 하고 재고 변경은 하지 않는다.
"""
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.base import utcnow

from app.models.menu import Menu
from app.models.recipe import RecipeItem


def list_menus(db: Session) -> list[Menu]:
    return list(db.execute(select(Menu).where(Menu.deleted_at.is_(None)).order_by(Menu.id)).scalars().all())


def get_menu(db: Session, menu_id: str, *, include_deleted: bool = False) -> Menu | None:
    menu = db.get(Menu, menu_id)
    if menu is not None and menu.deleted_at is not None and not include_deleted:
        return None
    return menu


def create_menu(db: Session, *, name: str, price: float, category: str | None, is_active: bool) -> Menu:
    menu = Menu(name=name, price=price, category=category, is_active=is_active)
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


def update_menu(db: Session, menu: Menu, *, name: str, price: float, category: str | None, is_active: bool) -> Menu:
    menu.name = name
    menu.price = price
    menu.category = category
    menu.is_active = is_active
    db.commit()
    db.refresh(menu)
    return menu


def soft_delete_menu(db: Session, menu: Menu) -> Menu:
    """deleted_at만 기록한다. is_active와 레시피, 과거 주문 참조는 건드리지 않는다."""
    menu.deleted_at = utcnow()
    db.commit()
    db.refresh(menu)
    return menu


def get_recipe(db: Session, menu_id: str) -> list[RecipeItem]:
    return list(db.execute(select(RecipeItem).where(RecipeItem.menu_id == menu_id)).scalars().all())


def replace_recipe(db: Session, menu_id: str, items: list[dict]) -> list[RecipeItem]:
    db.execute(delete(RecipeItem).where(RecipeItem.menu_id == menu_id))
    rows = [
        RecipeItem(menu_id=menu_id, ingredient_id=i["ingredient_id"], qty_per_unit=i["qty_per_unit"], unit=i["unit"])
        for i in items
    ]
    db.add_all(rows)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows
