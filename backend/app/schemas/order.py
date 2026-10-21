from pydantic import BaseModel, Field


class OrderItemIn(BaseModel):
    menu_id: str
    qty: int = Field(ge=1)


class OrderCreateIn(BaseModel):
    """손님 주문은 items만(테이블은 tableToken에서 식별), 직원 대리 주문은 table_id도 보낸다(계약 StaffOrderRequest)."""

    items: list[OrderItemIn]
    table_id: str | None = None


class StockWarningOut(BaseModel):
    ingredient_id: str
    name: str
    current_stock: float
    required: float


class OrderItemOut(BaseModel):
    id: str
    order_id: str
    menu_id: str
    menu_name: str
    qty: int
    price_snapshot: float
    item_status: str
    table_no: int | None = None


class OrderOut(BaseModel):
    id: str
    table_id: str
    table_no: int | None = None
    status: str
    total_amount: float
    created_at: str
    items: list[OrderItemOut]
    stock_warnings: list[StockWarningOut] = []


class OrderListOut(BaseModel):
    """계약 OrderListResponse. 커서 페이지네이션은 파일럿 범위에서 구현하지 않는다(항상 전체 반환)."""

    items: list[OrderOut]
    next_cursor: str | None = None
    has_more: bool = False


class OrderStatusIn(BaseModel):
    status: str


class ItemStatusIn(BaseModel):
    status: str


class ErrorOut(BaseModel):
    code: str | None = None
    detail: str
