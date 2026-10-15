// D-15: POST /orders는 Idempotency-Key(UUID) 헤더가 필수다.
// 같은 주문 시도(네트워크 재시도, 버튼 중복 클릭)는 같은 키를 재사용해야
// 서버가 기존 주문을 그대로 반환한다. 새 주문 시도는 새 키를 발급한다.
//
// 필드명/엔드포인트/헤더는 docs/api/openapi.yaml(계약)에서 생성한 schema.ts를
// 그대로 쓴다. 손으로 타입을 다시 쓰지 않는다 — 계약이 바뀌면
// `npm run gen:api`로 schema.ts를 재생성해서 타입 에러로 drift를 잡는다.

import type { components } from "./schema";

export type Order = components["schemas"]["Order"];
export type ErrorResponse = components["schemas"]["ErrorResponse"];

const BASE_URL = "/api/v1";
const IDEMPOTENCY_KEY_STORAGE_PREFIX = "pos:idempotency-key:";
const IDEMPOTENCY_KEY_MISMATCH = "IDEMPOTENCY_KEY_MISMATCH";

export interface CreateOrderRequestItem {
  menu_id: string;
  qty: number;
}

export interface CreateOrderRequest {
  items: CreateOrderRequestItem[];
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

async function parseErrorBody(res: Response): Promise<ErrorResponse | null> {
  try {
    return (await res.json()) as ErrorResponse;
  } catch {
    return null;
  }
}

export async function createOrder(
  draftId: string,
  tableSessionToken: string,
  payload: CreateOrderRequest,
  baseUrl = BASE_URL,
): Promise<Order> {
  const idempotencyKey = getOrCreateIdempotencyKey(draftId);

  const res = await fetch(`${baseUrl}/orders`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": idempotencyKey,
      "X-Table-Session-Token": tableSessionToken,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    if (res.status === 422) {
      const body = await parseErrorBody(res);
      // FastAPI는 요청 검증 실패에도 422를 반환한다. 같은 키·다른 본문일 때만
      // (code === IDEMPOTENCY_KEY_MISMATCH) 키를 버린다 — 그 외 검증 오류에서
      // 키를 지우면 다음 재시도가 새 키로 나가 중복 주문이 생긴다.
      if (body?.code === IDEMPOTENCY_KEY_MISMATCH) {
        clearIdempotencyKey(draftId);
      }
    }
    throw new Error(`CREATE_ORDER_FAILED: ${res.status}`);
  }

  // 성공 후에는 같은 draftId로의 재제출이 없으므로 키를 비워 메모리를 아낀다.
  clearIdempotencyKey(draftId);
  return res.json();
}

export async function fetchMyOrders(
  tableSessionToken: string,
  baseUrl = BASE_URL,
): Promise<Order[]> {
  const res = await fetch(`${baseUrl}/orders/mine`, {
    headers: { "X-Table-Session-Token": tableSessionToken },
  });
  if (!res.ok) {
    throw new Error(`FETCH_MY_ORDERS_FAILED: ${res.status}`);
  }
  return res.json();
}
