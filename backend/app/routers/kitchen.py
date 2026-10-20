from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import service as auth_service
from app.auth.dependencies import get_current_role
from app.db import get_db
from app.models.order import Order
from app.schemas.order import ItemStatusIn, OrderItemOut
from app.services import order_service

router = APIRouter(tags=["kitchen"])


@router.patch("/kitchen/items/{item_id}/status")
def patch_item_status(
    item_id: str, body: ItemStatusIn, _role=Depends(get_current_role), db: Session = Depends(get_db)
):
    try:
        item = order_service.change_item_status(db, item_id, body.status)
    except order_service.NotFound:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다") from None
    except order_service.InvalidTransition:
        raise HTTPException(status_code=409, detail="허용되지 않는 상태 전이") from None
    return {"item_id": item.id, "status": item.item_status}


@router.get("/kitchen/queue", response_model=list[OrderItemOut])
def kitchen_queue(
    limit: int = Query(default=50, ge=1, le=200),  # 계약 파라미터. 파일럿에서는 페이지네이션 없이 전체를 돌려준다.
    cursor: str | None = None,
    _role=Depends(get_current_role),
    db: Session = Depends(get_db),
):
    """조리 대기/진행 항목(주문 항목 단위). 계약상 응답은 래퍼 없는 배열이다."""
    items = order_service.kitchen_queue(db)
    table_ids = {i.order_id: db.get(Order, i.order_id).table_id for i in items}
    nos = auth_service.table_numbers(db, list(table_ids.values()))
    return [
        OrderItemOut(
            id=i.id,
            order_id=i.order_id,
            menu_id=i.menu_id,
            menu_name=i.menu_name,
            qty=i.qty,
            price_snapshot=float(i.price_snapshot),
            item_status=i.item_status,
            table_no=nos.get(table_ids[i.order_id]),
        )
        for i in items
    ]
