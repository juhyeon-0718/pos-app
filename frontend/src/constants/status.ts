// D-18: API 상태 값은 영문 코드. 한글 라벨은 여기서만 관리한다.

export type OrderStatus = "received" | "cooking" | "served" | "paid" | "cancelled";
export type ItemStatus = "pending" | "cooking" | "done";

export const ORDER_STATUS_LABEL: Record<OrderStatus, string> = {
  received: "접수",
  cooking: "조리중",
  served: "서빙완료",
  paid: "결제 완료", // U-03 명세 표기(D-33). 나머지 라벨은 F-11에서 정리
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

// 주방 화면 상태 변경 버튼 문구. "상태 라벨 + 으로 변경"처럼 조사를 붙이면 받침 유무에
// 따라 틀리므로(완료으로 변경 등) 동작 이름으로 고정한다. done은 다음 동작이 없다.
export const ITEM_ACTION_LABEL: Record<ItemStatus, string | null> = {
  pending: "조리 시작", // pending -> cooking
  cooking: "조리 완료", // cooking -> done
  done: null,
};

export function itemActionLabel(status: ItemStatus): string | null {
  return ITEM_ACTION_LABEL[status];
}
