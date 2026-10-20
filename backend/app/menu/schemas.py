from pydantic import BaseModel


class MenuOut(BaseModel):
    id: str
    name: str
    price: float
    category: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class MenuListOut(BaseModel):
    """계약 MenuListResponse. 커서 페이지네이션은 파일럿 범위에서 구현하지 않는다(항상 전체 반환)."""

    items: list[MenuOut]
    next_cursor: str | None = None
    has_more: bool = False


class MenuWriteIn(BaseModel):
    name: str
    price: float
    category: str | None = None
    is_active: bool = True


class RecipeItemIn(BaseModel):
    ingredient_id: str
    qty_per_unit: float
    unit: str


class RecipeItemOut(BaseModel):
    ingredient_id: str
    qty_per_unit: float
    unit: str

    model_config = {"from_attributes": True}
