from datetime import datetime

from pydantic import BaseModel


class IngredientOut(BaseModel):
    id: str
    name: str
    unit: str
    current_stock: float
    safety_stock: float
    lead_time_days: int
    unit_price: float
    is_active: bool


class IngredientWriteIn(BaseModel):
    name: str
    unit: str
    safety_stock: float = 0
    lead_time_days: int = 0
    unit_price: float = 0


class StockMovementOut(BaseModel):
    id: str
    ingredient_id: str
    qty_delta: float
    type: str
    ref_id: str | None = None
    created_at: datetime


class MovementCreateIn(BaseModel):
    qty_delta: float
    type: str
    ref_id: str | None = None
