from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_role, require_any_auth, require_owner
from app.db import get_db
from app.menu import service
from app.menu.schemas import MenuListOut, MenuOut, MenuWriteIn, RecipeItemIn, RecipeItemOut

router = APIRouter(tags=["menus"])


def _menu_out(menu) -> MenuOut:
    return MenuOut.model_validate(menu)


@router.get("/menus", response_model=MenuListOut)
def list_menus(db: Session = Depends(get_db), _auth=Depends(require_any_auth)):
    return MenuListOut(items=[_menu_out(m) for m in service.list_menus(db)])


@router.post("/menus", response_model=MenuOut, status_code=201)
def create_menu(body: MenuWriteIn, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    menu = service.create_menu(db, name=body.name, price=body.price, category=body.category, is_active=body.is_active)
    return _menu_out(menu)


@router.patch("/menus/{menu_id}", response_model=MenuOut)
def update_menu(menu_id: str, body: MenuWriteIn, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    try:
        menu = service.update_menu(
            db, menu_id, name=body.name, price=body.price, category=body.category, is_active=body.is_active
        )
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return _menu_out(menu)


@router.delete("/menus/{menu_id}", status_code=204)
def deactivate_menu(menu_id: str, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    try:
        service.deactivate_menu(db, menu_id)
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None


@router.get("/menus/{menu_id}/recipe", response_model=list[RecipeItemOut])
def get_menu_recipe(menu_id: str, db: Session = Depends(get_db), _role=Depends(get_current_role)):
    try:
        items = service.get_recipe(db, menu_id)
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return [RecipeItemOut.model_validate(i) for i in items]


@router.put("/menus/{menu_id}/recipe", response_model=list[RecipeItemOut])
def put_menu_recipe(
    menu_id: str, body: list[RecipeItemIn], db: Session = Depends(get_db), _owner=Depends(require_owner)
):
    try:
        items = service.replace_recipe(db, menu_id, [i.model_dump() for i in body])
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return [RecipeItemOut.model_validate(i) for i in items]
