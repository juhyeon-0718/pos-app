"""menu 모듈 업무 로직. 라우터는 이 모듈의 함수만 호출한다 (D-25)."""
from sqlalchemy.orm import Session

from app.menu import repository
from app.models.menu import Menu
from app.models.recipe import RecipeItem


class NotFound(Exception):
    pass


def list_menus(db: Session) -> list[Menu]:
    return repository.list_menus(db)


def create_menu(db: Session, *, name: str, price: float, category: str | None, is_active: bool) -> Menu:
    return repository.create_menu(db, name=name, price=price, category=category, is_active=is_active)


def update_menu(db: Session, menu_id: str, *, name: str, price: float, category: str | None, is_active: bool) -> Menu:
    menu = repository.get_menu(db, menu_id)
    if menu is None:
        raise NotFound(f"메뉴를 찾을 수 없습니다: {menu_id}")
    return repository.update_menu(db, menu, name=name, price=price, category=category, is_active=is_active)


def deactivate_menu(db: Session, menu_id: str) -> Menu:
    menu = repository.get_menu(db, menu_id)
    if menu is None:
        raise NotFound(f"메뉴를 찾을 수 없습니다: {menu_id}")
    return repository.deactivate_menu(db, menu)


def get_recipe(db: Session, menu_id: str) -> list[RecipeItem]:
    menu = repository.get_menu(db, menu_id)
    if menu is None:
        raise NotFound(f"메뉴를 찾을 수 없습니다: {menu_id}")
    return repository.get_recipe(db, menu_id)


def replace_recipe(db: Session, menu_id: str, items: list[dict]) -> list[RecipeItem]:
    menu = repository.get_menu(db, menu_id)
    if menu is None:
        raise NotFound(f"메뉴를 찾을 수 없습니다: {menu_id}")
    return repository.replace_recipe(db, menu_id, items)
