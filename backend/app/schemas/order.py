from pydantic import BaseModel, Field


class OrderItemIn(BaseModel):
    menu_id: str
    qty: int = Field(ge=1)


class OrderCreateIn(BaseModel):
    items: list[OrderItemIn]


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


class OrderOut(BaseModel):
    id: str
    table_id: str
    status: str
    total_amount: float
    created_at: str
    items: list[OrderItemOut]
    stock_warnings: list[StockWarningOut] = []


class OrderStatusIn(BaseModel):
    status: str


class ItemStatusIn(BaseModel):
    status: str


class ErrorOut(BaseModel):
    code: str | None = None
    detail: str
