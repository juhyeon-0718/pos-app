from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import service as auth_service
from app.auth.dependencies import TableSession, get_current_role, get_table_id, get_table_session
from app.db import get_db
from app.models.enums import OrderStatus, Role
from app.models.order import Order
from app.schemas.order import OrderCreateIn, OrderListOut, OrderOut, OrderStatusIn
from app.services import order_service

router = APIRouter(tags=["orders"])


def _serialize(order: Order, table_no: int | None = None) -> dict:
    return {
        "id": order.id,
        "table_id": order.table_id,
        "table_no": table_no,
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
                "table_no": table_no,
            }
            for item in order.items
        ],
        "stock_warnings": getattr(order, "_stock_warnings", []) or [],
    }


def _resolve_order_table(db: Session, body: OrderCreateIn, authorization: str | None, table_token: str | None) -> str:
    """손님(tableToken)은 세션의 테이블, 직원·사장(bearer)은 body.table_id로 주문한다(계약 createOrder)."""
    if authorization:
        role = get_current_role(authorization)
        if role not in (Role.staff, Role.owner):
            raise HTTPException(status_code=403, detail="주문을 대신 입력할 권한이 없습니다")
        if not body.table_id:
            raise HTTPException(status_code=422, detail="직원 대리 주문에는 table_id가 필요합니다")
        if body.table_id not in auth_service.table_numbers(db, [body.table_id]):
            raise HTTPException(status_code=404, detail="테이블을 찾을 수 없습니다")
        return body.table_id
    if table_token:
        own = get_table_id(table_token, db)
        if body.table_id and body.table_id != own:
            raise HTTPException(status_code=422, detail="손님 주문에는 table_id를 보낼 수 없습니다")
        return own
    raise HTTPException(status_code=401, detail="인증이 필요합니다")


def _out(db: Session, order: Order) -> dict:
    """주문 응답에 테이블 번호(table_no)를 채운다. 번호는 auth 모듈 공개 service로만 조회한다."""
    return _serialize(order, auth_service.table_numbers(db, [order.table_id]).get(order.table_id))


def _out_many(db: Session, orders: list[Order]) -> list[dict]:
    nos = auth_service.table_numbers(db, [o.table_id for o in orders])
    return [_serialize(o, nos.get(o.table_id)) for o in orders]


@router.post("/orders", response_model=OrderOut, status_code=201)
def create_order(
    body: OrderCreateIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    authorization: str | None = Header(default=None),
    x_table_session_token: str | None = Header(default=None, alias="X-Table-Session-Token"),
    db: Session = Depends(get_db),
):
    if not idempotency_key:
        raise HTTPException(status_code=422, detail="Idempotency-Key 헤더가 필요합니다")
    table_id = _resolve_order_table(db, body, authorization, x_table_session_token)
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
    except order_service.MenuUnavailable as exc:
        # 계약 Error 스키마({code, detail})를 응답 최상위에 둔다.
        return JSONResponse(
            status_code=409,
            content={"code": "MENU_UNAVAILABLE", "detail": f"품절되었거나 삭제된 메뉴가 있어 주문할 수 없습니다: {exc}"},
        )
    except order_service.NotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return _out(db, order)


@router.get("/orders/mine", response_model=list[OrderOut])
def my_orders(session: TableSession = Depends(get_table_session), db: Session = Depends(get_db)):
    orders = order_service.list_table_orders(db, session.table_id, session_issued_at=session.issued_at)
    return _out_many(db, orders)


@router.get("/orders", response_model=OrderListOut)
def list_orders(
    status: OrderStatus | None = None,
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=200),  # 계약 파라미터. 파일럿에서는 페이지네이션 없이 전체를 돌려준다.
    cursor: str | None = None,
    _role=Depends(get_current_role),
    db: Session = Depends(get_db),
):
    orders = order_service.list_orders(db, status=status.value if status else None, from_=from_, to=to)
    return {"items": _out_many(db, orders), "next_cursor": None, "has_more": False}


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
    return _out(db, order)


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(
    order_id: str,
    authorization: str | None = Header(default=None),
    x_table_session_token: str | None = Header(default=None, alias="X-Table-Session-Token"),
    db: Session = Depends(get_db),
):
    """직원/주방/사장(bearer)은 모든 주문, 손님(tableToken)은 자기 테이블 주문만 본다."""
    own_table_id: str | None = None
    if authorization:
        get_current_role(authorization)
    elif x_table_session_token:
        own_table_id = get_table_id(x_table_session_token, db)
    else:
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    try:
        order = order_service.get_order(db, order_id)
    except order_service.NotFound:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다") from None
    if own_table_id is not None and order.table_id != own_table_id:
        # 다른 테이블의 주문은 존재 여부도 알려 주지 않는다.
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return _out(db, order)
