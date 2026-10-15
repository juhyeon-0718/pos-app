// D-18: API 상태 값은 영문 코드. 한글 라벨은 여기서만 관리한다.

export type OrderStatus = "received" | "cooking" | "served" | "paid" | "cancelled";
export type ItemStatus = "pending" | "cooking" | "done";

export const ORDER_STATUS_LABEL: Record<OrderStatus, string> = {
  received: "접수",
  cooking: "조리중",
  served: "서빙완료",
  paid: "결제완료",
  cancelled: "취소됨",
};

export const ITEM_STATUS_LABEL: Record<ItemStatus, string> = {
  pending: "대기",
  cooking: "조리중",
  done: "완료",
};

export function orderStatusLabel(status: OrderStatus): string {
  return ORDER_STATUS_LABEL[status] ?? status;
}

export function itemStatusLabel(status: ItemStatus): string {
  return ITEM_STATUS_LABEL[status] ?? status;
}
