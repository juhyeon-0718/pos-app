from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import require_owner
from app.db import get_db
from app.inventory import service
from app.inventory.schemas import (
    IngredientListOut,
    IngredientOut,
    IngredientWriteIn,
    MovementCreateIn,
    StockMovementListOut,
    StockMovementOut,
)
from app.models.ingredient import Ingredient

router = APIRouter(tags=["ingredients"])


def _ingredient_out(ingredient: Ingredient, current_stock: float) -> IngredientOut:
    return IngredientOut(
        id=ingredient.id,
        name=ingredient.name,
        unit=ingredient.unit,
        current_stock=current_stock,
        safety_stock=float(ingredient.safety_stock),
        lead_time_days=ingredient.lead_time_days,
        unit_price=float(ingredient.unit_price),
        is_active=ingredient.is_active,
    )


def _movement_out(movement) -> StockMovementOut:
    return StockMovementOut(
        id=movement.id,
        ingredient_id=movement.ingredient_id,
        qty_delta=float(movement.qty_delta),
        type=movement.reason,
        ref_id=movement.ref_id,
        created_at=movement.created_at,
    )


@router.get("/ingredients", response_model=IngredientListOut)
def list_ingredients(db: Session = Depends(get_db), _owner=Depends(require_owner)):
    return IngredientListOut(
        items=[_ingredient_out(ing, stock) for ing, stock in service.list_ingredients_with_stock(db)]
    )


@router.post("/ingredients", response_model=IngredientOut, status_code=201)
def create_ingredient(body: IngredientWriteIn, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    ingredient = service.create_ingredient(
        db,
        name=body.name,
        unit=body.unit,
        safety_stock=body.safety_stock,
        lead_time_days=body.lead_time_days,
        unit_price=body.unit_price,
    )
    return _ingredient_out(ingredient, 0.0)


@router.patch("/ingredients/{ingredient_id}", response_model=IngredientOut)
def update_ingredient(
    ingredient_id: str, body: IngredientWriteIn, db: Session = Depends(get_db), _owner=Depends(require_owner)
):
    try:
        ingredient = service.update_ingredient(
            db,
            ingredient_id,
            name=body.name,
            unit=body.unit,
            safety_stock=body.safety_stock,
            lead_time_days=body.lead_time_days,
            unit_price=body.unit_price,
        )
        _, current = service.get_ingredient_with_stock(db, ingredient_id)
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return _ingredient_out(ingredient, current)


@router.delete("/ingredients/{ingredient_id}", response_model=IngredientOut)
def deactivate_ingredient(ingredient_id: str, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    try:
        ingredient = service.deactivate_ingredient(db, ingredient_id)
        _, current = service.get_ingredient_with_stock(db, ingredient_id)
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except service.Conflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return _ingredient_out(ingredient, current)


@router.get("/ingredients/{ingredient_id}/movements", response_model=StockMovementListOut)
def list_movements(ingredient_id: str, db: Session = Depends(get_db), _owner=Depends(require_owner)):
    try:
        movements = service.list_movements(db, ingredient_id)
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return StockMovementListOut(items=[_movement_out(m) for m in movements])


@router.post("/ingredients/{ingredient_id}/movements", response_model=StockMovementOut, status_code=201)
def create_movement(
    ingredient_id: str, body: MovementCreateIn, db: Session = Depends(get_db), _owner=Depends(require_owner)
):
    try:
        movement = service.create_movement(
            db, ingredient_id, qty_delta=body.qty_delta, type_=body.type, ref_id=body.ref_id
        )
    except service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except service.Conflict as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return _movement_out(movement)
