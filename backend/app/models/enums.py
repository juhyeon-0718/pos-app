"""
pos-app 도메인 공통 enum (D-18, D-19). DB 컬럼은 문자열로 저장하고
애플리케이션 레벨에서 값을 검증한다 (DB 네이티브 ENUM 타입은 쓰지 않아
마이그레이션에서 값 추가/변경이 가볍다).
"""
from enum import Enum


class OrderStatus(str, Enum):
    received = "received"
    cooking = "cooking"
    served = "served"
    paid = "paid"
    cancelled = "cancelled"


class ItemStatus(str, Enum):
    pending = "pending"
    cooking = "cooking"
    done = "done"


class StockMovementReason(str, Enum):
    order_deduction = "order_deduction"
    cancel_restore = "cancel_restore"
    disposal = "disposal"
    restock = "restock"
    adjustment = "adjustment"
    purchase_restock = "purchase_restock"


class Role(str, Enum):
    staff = "staff"
    kitchen = "kitchen"
    owner = "owner"


# 조리 단계에 들어선 것으로 보는 항목 상태 (조리 후 취소 판단 기준, Q1 공통 주의사항)
COOKING_STAGE_ITEM_STATUSES = {ItemStatus.cooking, ItemStatus.done}
