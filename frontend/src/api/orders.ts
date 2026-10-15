// D-15: POST /orders는 Idempotency-Key(UUID) 헤더가 필수다.
// 같은 주문 시도(네트워크 재시도, 버튼 중복 클릭)는 같은 키를 재사용해야
// 서버가 기존 주문을 그대로 반환한다. 새 주문 시도는 새 키를 발급한다.

import type { OrderStatus, ItemStatus } from "../constants/status";

const IDEMPOTENCY_KEY_STORAGE_PREFIX = "pos:idempotency-key:";

export interface OrderItemInput {
  menuItemId: string;
  quantity: number;
}

export interface CreateOrderRequest {
  tableToken: string;
  items: OrderItemInput[];
}

export interface StockWarning {
  ingredientId: string;
  currentStock: number;
  requiredAmount: number;
}

export interface OrderItemResponse {
  id: string;
  menuItemId: string;
  quantity: number;
  status: ItemStatus;
}

export interface OrderResponse {
  id: string;
  status: OrderStatus;
  items: OrderItemResponse[];
  stockWarnings: StockWarning[];
}

/**
 * draftId는 "이 장바구니 제출 시도"를 식별하는 클라이언트 생성 id다.
 * 같은 draftId로 재시도하면 같은 Idempotency-Key를 재사용한다.
 * 장바구니를 비우고 새로 담아 제출하면 새 draftId를 써서 새 키를 발급받아야 한다.
 */
export function getOrCreateIdempotencyKey(draftId: string): string {
  const storageKey = `${IDEMPOTENCY_KEY_STORAGE_PREFIX}${draftId}`;
  const existing = sessionStorage.getItem(storageKey);
  if (existing) return existing;

  const key = crypto.randomUUID();
  sessionStorage.setItem(storageKey, key);
  return key;
}

export function clearIdempotencyKey(draftId: string): void {
  sessionStorage.removeItem(`${IDEMPOTENCY_KEY_STORAGE_PREFIX}${draftId}`);
}

export async function createOrder(
  draftId: string,
  payload: CreateOrderRequest,
  baseUrl = "/api",
): Promise<OrderResponse> {
  const idempotencyKey = getOrCreateIdempotencyKey(draftId);

  const res = await fetch(`${baseUrl}/orders`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": idempotencyKey,
    },
    body: JSON.stringify(payload),
  });

  if (res.status === 422) {
    // 같은 키로 다른 본문을 보냄: 새 주문 시도로 간주하고 키를 새로 발급해 재시도하게 한다.
    clearIdempotencyKey(draftId);
    throw new Error("IDEMPOTENCY_KEY_CONFLICT");
  }

  if (!res.ok) {
    throw new Error(`CREATE_ORDER_FAILED: ${res.status}`);
  }

  // 성공 후에는 같은 draftId로의 재제출이 없으므로 키를 비워 메모리를 아낀다.
  clearIdempotencyKey(draftId);
  return res.json();
}

export async function fetchMyOrders(
  tableToken: string,
  baseUrl = "/api",
): Promise<OrderResponse[]> {
  const res = await fetch(`${baseUrl}/orders/mine`, {
    headers: { Authorization: `TableToken ${tableToken}` },
  });
  if (!res.ok) {
    throw new Error(`FETCH_MY_ORDERS_FAILED: ${res.status}`);
  }
  return res.json();
}
