"""
주문 생성/상태 전이 핵심 로직 (D-14~D-19).
계산(통계/추천량)은 이 서비스 범위가 아니다 — purchase-forecast-stats 스킬 참고.
"""
import hashlib
import json
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.base import gen_id
from app.models.enums import COOKING_STAGE_ITEM_STATUSES, ItemStatus, OrderStatus, Role, StockMovementReason
from app.models.idempotency_key import IdempotencyKey
from app.models.ingredient import Ingredient
from app.models.order import Order, OrderItem
from app.menu import service as menu_service
from app.models.recipe import RecipeItem
from app.services import stock_service


class IdempotencyConflict(Exception):
    """같은 키로 본문이 다른 요청이 들어옴 (422)."""


class NotFound(Exception):
    pass


class Forbidden(Exception):
    pass


class MenuUnavailable(Exception):
    """일시품절이거나 삭제된 메뉴가 주문에 포함됨 (409, D-37). 메시지는 해당 메뉴 이름들."""


class InvalidTransition(Exception):
    """허용되지 않는 상태 전이 (409). 메시지가 있으면 응답 detail로 쓴다."""


class ServeConditionNotMet(InvalidTransition):
    """served 전이 조건(모든 항목 done, D-32) 불충족 (409)."""


@dataclass
class StockWarningHook:
    """
    B1 범위: SSE는 발행하지 않는다. 서비스 레이어에 훅만 둬서 B2에서
    실제 SSE 발행 함수로 교체할 수 있게 한다 (리드 지시: '인터페이스만').
    """
    warnings: list[dict] = field(default_factory=list)

    def emit(self, order_id: str, ingredient_id: str, name: str, current_stock: float, required: float) -> None:
        # B2 이후: 여기서 SSE stock.warning 이벤트를 발행한다.
        self.warnings.append(
            {
                "order_id": order_id,
                "ingredient_id": ingredient_id,
                "name": name,
                "current_stock": current_stock,
                "required": required,
            }
        )


def _body_hash(items: list[dict]) -> str:
    canonical = json.dumps(items, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_order(
    db: Session,
    table_id: str,
    items_in: list[dict],
    idempotency_key: str,
    stock_hook: StockWarningHook | None = None,
) -> Order:
    stock_hook = stock_hook or StockWarningHook()
    req_hash = _body_hash(items_in)

    existing = db.get(IdempotencyKey, idempotency_key)
    if existing is not None:
        if existing.request_hash != req_hash:
            raise IdempotencyConflict()
        order = db.get(Order, existing.order_id)
        if order is None:
            raise NotFound()
        return order

    # D-37: 쓰기 전에 모든 메뉴를 먼저 검증한다. 메뉴 상태는 menu 모듈 공개 service로만 조회한다.
    menus = {}
    unavailable: list[str] = []
    for item_in in items_in:
        try:
            menus[item_in["menu_id"]] = menu_service.get_orderable_menu(db, item_in["menu_id"])
        except menu_service.NotFound as exc:
            raise NotFound(str(exc)) from None
        except menu_service.Unavailable as exc:
            unavailable.append(str(exc))
    if unavailable:
        raise MenuUnavailable(", ".join(dict.fromkeys(unavailable)))

    # 신규 생성 시도. 동시 요청(TC-01) 대비: idempotency_keys.key 유니크 제약으로
    # 레이스를 막고, 경쟁에서 진 요청은 IntegrityError를 잡아 승자의 주문을 반환한다.
    order = Order(id=gen_id("o"), table_id=table_id, status=OrderStatus.received.value, total_amount=0)
    db.add(order)

    total_amount = 0.0
    stock_warnings: list[dict] = []
    for item_in in items_in:
        menu = menus[item_in["menu_id"]]
        qty = int(item_in["qty"])
        order_item = OrderItem(
            order_id=order.id,
            menu_id=menu.id,
            menu_name=menu.name,
            qty=qty,
            price_snapshot=float(menu.price),
            item_status=ItemStatus.pending.value,
        )
        order.items.append(order_item)
        total_amount += float(menu.price) * qty

        recipe_rows = db.execute(select(RecipeItem).where(RecipeItem.menu_id == menu.id)).scalars().all()
        for recipe in recipe_rows:
            required_qty = float(recipe.qty_per_unit) * qty
            # D-21: 동시 주문(TC-01)에서 같은 식재료 차감이 레이스 없이 순서대로
            # 반영되도록 ingredients 행을 먼저 잠근다 (PostgreSQL FOR UPDATE).
            stock_service.lock_ingredient_for_update(db, recipe.ingredient_id)
            before_stock = stock_service.current_stock(db, recipe.ingredient_id)
            # 재고가 부족해도 주문 생성은 막지 않는다 (D-07/D-14). 음수 재고를 허용한다.
            stock_service.record_movement(
                db, recipe.ingredient_id, -required_qty, StockMovementReason.order_deduction, ref_id=order.id
            )
            if before_stock < required_qty:
                ingredient = db.get(Ingredient, recipe.ingredient_id)
                warning = {
                    "ingredient_id": recipe.ingredient_id,
                    "name": ingredient.name if ingredient else recipe.ingredient_id,
                    "current_stock": before_stock,
                    "required": required_qty,
                }
                stock_warnings.append(warning)
                stock_hook.emit(order.id, **warning)

    order.total_amount = total_amount
    order._stock_warnings = stock_warnings  # 응답 직렬화용, DB 컬럼 아님

    key_row = IdempotencyKey(key=idempotency_key, order_id=order.id, request_hash=req_hash)
    db.add(key_row)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # 동시에 같은 키로 들어온 다른 요청이 먼저 커밋한 경우: 그 결과를 반환한다.
        winner = db.get(IdempotencyKey, idempotency_key)
        if winner is None:
            raise
        winner_order = db.get(Order, winner.order_id)
        if winner_order is None:
            raise NotFound() from None
        return winner_order

    db.refresh(order)
    order._stock_warnings = stock_warnings
    return order


def _order_reached_cooking_stage(order: Order) -> bool:
    return any(ItemStatus(item.item_status) in COOKING_STAGE_ITEM_STATUSES for item in order.items)


def _all_items_done(order: Order) -> bool:
    """D-32: 모든 항목이 done이어야 한다. 항목이 없으면 False. (항목 단위 취소는 2차, D-35)"""
    return bool(order.items) and all(i.item_status == ItemStatus.done.value for i in order.items)


def change_order_status(db: Session, order_id: str, new_status: str, role: Role) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise NotFound()

    try:
        target = OrderStatus(new_status)
    except ValueError:
        raise InvalidTransition() from None

    if target == OrderStatus.served and not _all_items_done(order):
        raise ServeConditionNotMet("모든 항목이 완료(done)되어야 서빙완료할 수 있습니다")

    if target == OrderStatus.cancelled:
        if _order_reached_cooking_stage(order):
            if role != Role.owner:
                raise Forbidden("조리 후 취소는 사장만 가능합니다")
            # D-19: cancel_restore(+)와 disposal(-)을 한 쌍으로 같은 트랜잭션에 기록 (순 변화 0)
            for qty_delta, reason in _order_ingredient_deltas(db, order):
                stock_service.record_movement(db, qty_delta[0], qty_delta[1], reason, ref_id=order.id)
        else:
            if role not in (Role.staff, Role.owner):
                raise Forbidden("취소 권한이 없습니다")
            for ingredient_id, required_qty in _order_ingredient_requirements(db, order):
                stock_service.record_movement(
                    db, ingredient_id, required_qty, StockMovementReason.cancel_restore, ref_id=order.id
                )
        order.status = OrderStatus.cancelled.value
    else:
        order.status = target.value

    db.commit()
    db.refresh(order)
    order._stock_warnings = []
    return order


def _order_ingredient_requirements(db: Session, order: Order) -> list[tuple[str, float]]:
    """주문 항목별 레시피 기준 필요량을 식재료 단위로 합산한다."""
    totals: dict[str, float] = {}
    for item in order.items:
        recipe_rows = db.execute(select(RecipeItem).where(RecipeItem.menu_id == item.menu_id)).scalars().all()
        for recipe in recipe_rows:
            totals[recipe.ingredient_id] = totals.get(recipe.ingredient_id, 0) + float(recipe.qty_per_unit) * item.qty
    return list(totals.items())


def _order_ingredient_deltas(db: Session, order: Order):
    """조리 후 취소: (ingredient_id, required_qty) 쌍마다 cancel_restore(+)/disposal(-)을 만든다."""
    pairs = []
    for ingredient_id, required_qty in _order_ingredient_requirements(db, order):
        pairs.append(((ingredient_id, required_qty), StockMovementReason.cancel_restore))
        pairs.append(((ingredient_id, -required_qty), StockMovementReason.disposal))
    return pairs


def change_item_status(db: Session, item_id: str, new_status: str) -> OrderItem:
    item = db.get(OrderItem, item_id)
    if item is None:
        raise NotFound()
    try:
        target = ItemStatus(new_status)
    except ValueError:
        raise InvalidTransition() from None

    item.item_status = target.value

    order = db.get(Order, item.order_id)
    # D-16: 항목 하나라도 cooking이면 주문은 서비스 레이어가 같은 트랜잭션에서 cooking으로 맞춘다.
    # served/paid는 직원이 주문 단위로 수동 변경한다 (여기서 자동으로 올리지 않음).
    if target == ItemStatus.cooking and order.status == OrderStatus.received.value:
        order.status = OrderStatus.cooking.value

    db.commit()
    db.refresh(item)
    return item
