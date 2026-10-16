"""모든 모델을 한 곳에서 import해 Base.metadata/alembic autogenerate가 전부 인식하게 한다."""
from app.models.menu import Menu  # noqa: F401
from app.models.ingredient import Ingredient  # noqa: F401
from app.models.recipe import RecipeItem  # noqa: F401
from app.models.stock_movement import StockMovement  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.idempotency_key import IdempotencyKey  # noqa: F401
