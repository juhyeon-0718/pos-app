from pydantic import BaseModel


class MenuOut(BaseModel):
    id: str
    name: str
    price: float
    category: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


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
