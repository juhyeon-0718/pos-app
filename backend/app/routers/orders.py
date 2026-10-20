from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_role, get_table_id
from app.db import get_db
from app.models.order import Order
from app.schemas.order import OrderCreateIn, OrderOut, OrderStatusIn
from app.services import order_service

router = APIRouter(tags=["orders"])


def _serialize(order: Order) -> dict:
    return {
        "id": order.id,
        "table_id": order.table_id,
        "status": order.status,
        "total_amount": float(order.total_amount),
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "id": item.id,
                "order_id": item.order_id,
                "menu_id": item.menu_id,
                "menu_name": item.menu_name,
                "qty": item.qty,
                "price_snapshot": float(item.price_snapshot),
                "item_status": item.item_status,
            }
            for item in order.items
        ],
        "stock_warnings": getattr(order, "_stock_warnings", []) or [],
    }


@router.post("/orders", response_model=OrderOut, status_code=201)
def create_order(
    body: OrderCreateIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    table_id: str = Depends(get_table_id),
    db: Session = Depends(get_db),
):
    if not idempotency_key:
        raise HTTPException(status_code=422, detail="Idempotency-Key 헤더가 필요합니다")
    try:
        order = order_service.create_order(
            db,
            table_id=table_id,
            items_in=[item.model_dump() for item in body.items],
            idempotency_key=idempotency_key,
        )
    except order_service.IdempotencyConflict:
        raise HTTPException(
            status_code=422,
            detail={"code": "IDEMPOTENCY_KEY_MISMATCH", "detail": "Idempotency-Key conflict: request body differs from original"},
        ) from None
    except order_service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return _serialize(order)


@router.get("/orders/mine", response_model=list[OrderOut])
def my_orders(table_id: str = Depends(get_table_id), db: Session = Depends(get_db)):
    orders = db.execute(select(Order).where(Order.table_id == table_id)).scalars().all()
    return [_serialize(o) for o in orders]


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
def patch_order_status(
    order_id: str,
    body: OrderStatusIn,
    role=Depends(get_current_role),
    db: Session = Depends(get_db),
):
    try:
        order = order_service.change_order_status(db, order_id, body.status, role)
    except order_service.NotFound:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다") from None
    except order_service.Forbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except order_service.ServeConditionNotMet as exc:
        # 계약 Error 스키마({code, detail})를 응답 최상위에 둔다.
        return JSONResponse(status_code=409, content={"code": "ORDER_ITEMS_NOT_DONE", "detail": str(exc)})
    except order_service.InvalidTransition:
        raise HTTPException(status_code=409, detail="허용되지 않는 상태 전이") from None
    return _serialize(order)
