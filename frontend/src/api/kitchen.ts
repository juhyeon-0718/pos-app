// GET /kitchen/queue: 조리 대기/진행 목록 (주문 항목 단위).
// PATCH /kitchen/items/{item_id}/status: pending -> cooking -> done 전이.

import type { components } from "./schema";

export type OrderItem = components["schemas"]["OrderItem"];
export type ItemStatus = "pending" | "cooking" | "done";

const BASE_URL = "/api/v1";

export async function fetchKitchenQueue(
  accessToken: string,
  baseUrl = BASE_URL,
): Promise<OrderItem[]> {
  const res = await fetch(`${baseUrl}/kitchen/queue`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!res.ok) {
    throw new Error(`FETCH_KITCHEN_QUEUE_FAILED: ${res.status}`);
  }
  return res.json();
}

export async function updateKitchenItemStatus(
  accessToken: string,
  itemId: string,
  status: ItemStatus,
  baseUrl = BASE_URL,
): Promise<void> {
  const res = await fetch(`${baseUrl}/kitchen/items/${itemId}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    throw new Error(`UPDATE_KITCHEN_ITEM_STATUS_FAILED: ${res.status}`);
  }
}
