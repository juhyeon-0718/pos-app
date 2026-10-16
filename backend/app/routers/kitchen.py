from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.order import ItemStatusIn
from app.services import order_service

router = APIRouter(tags=["kitchen"])


@router.patch("/kitchen/items/{item_id}/status")
def patch_item_status(item_id: str, body: ItemStatusIn, db: Session = Depends(get_db)):
    try:
        item = order_service.change_item_status(db, item_id, body.status)
    except order_service.NotFound:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다") from None
    except order_service.InvalidTransition:
        raise HTTPException(status_code=409, detail="허용되지 않는 상태 전이") from None
    return {"item_id": item.id, "status": item.item_status}
