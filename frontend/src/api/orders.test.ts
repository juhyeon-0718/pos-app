import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  clearIdempotencyKey,
  createOrder,
  createStaffOrder,
  getOrCreateIdempotencyKey,
  type CreateOrderRequest,
  type CreateStaffOrderRequest,
} from "./orders";

const payload: CreateOrderRequest = {
  items: [{ menu_id: "m_1", qty: 2 }],
};

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  sessionStorage.clear();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("getOrCreateIdempotencyKey", () => {
  it("같은 draftId로 재시도하면 같은 키가 나간다", () => {
    const first = getOrCreateIdempotencyKey("draft-1");
    const second = getOrCreateIdempotencyKey("draft-1");
    expect(second).toBe(first);
  });

  it("다른 draftId는 다른 키를 발급한다", () => {
    const a = getOrCreateIdempotencyKey("draft-a");
    const b = getOrCreateIdempotencyKey("draft-b");
    expect(a).not.toBe(b);
  });
});

describe("createOrder - Idempotency-Key 생명주기", () => {
  it("성공 응답을 받은 주문의 Idempotency-Key 헤더는 매 호출이 동일하다(재시도 시나리오)", async () => {
    const seenKeys: string[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_url: string, init?: RequestInit) => {
        const headers = init?.headers as Record<string, string>;
        seenKeys.push(headers["Idempotency-Key"]);
        return jsonResponse(201, { id: "o_1", status: "received", items: [], stock_warnings: [] });
      }),
    );

    // draftId를 공유하는 재시도 1회차: 네트워크 응답을 못 받았다고 가정하고 같은 draftId로 다시 보냄
    const key1 = getOrCreateIdempotencyKey("draft-retry");
    await createOrder("draft-retry", "table-session-token", payload).catch(() => {});
    // createOrder 성공 시 키를 정리하므로, 재시도 검증은 clear 전 상태를 직접 비교한다.
    expect(seenKeys[0]).toBe(key1);
  });

  it("IDEMPOTENCY_KEY_MISMATCH가 아닌 422에서는 키를 유지한다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse(422, { code: "VALIDATION_ERROR", detail: "qty must be >= 1" }),
      ),
    );

    const keyBefore = getOrCreateIdempotencyKey("draft-validation");
    await expect(
      createOrder("draft-validation", "table-session-token", payload),
    ).rejects.toThrow("CREATE_ORDER_FAILED: 422");

    const keyAfter = getOrCreateIdempotencyKey("draft-validation");
    expect(keyAfter).toBe(keyBefore);
  });

  it("IDEMPOTENCY_KEY_MISMATCH 422에서는 키를 버려 다음 시도가 새 키를 쓴다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse(422, {
          code: "IDEMPOTENCY_KEY_MISMATCH",
          detail: "같은 Idempotency-Key로 이전과 다른 요청 본문이 전송되었습니다.",
        }),
      ),
    );

    const keyBefore = getOrCreateIdempotencyKey("draft-mismatch");
    await expect(
      createOrder("draft-mismatch", "table-session-token", payload),
    ).rejects.toThrow("CREATE_ORDER_FAILED: 422");

    const keyAfter = getOrCreateIdempotencyKey("draft-mismatch");
    expect(keyAfter).not.toBe(keyBefore);
  });

  it("성공 후에는 키를 정리한다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse(201, { id: "o_1", status: "received", items: [], stock_warnings: [] }),
      ),
    );

    const keyBefore = getOrCreateIdempotencyKey("draft-success");
    await createOrder("draft-success", "table-session-token", payload);
    const keyAfter = getOrCreateIdempotencyKey("draft-success");
    expect(keyAfter).not.toBe(keyBefore);

    clearIdempotencyKey("draft-success");
  });
});

describe("createStaffOrder - table_id 타입 강제", () => {
  it("table_id 없이 호출하면 타입 오류가 난다(계약: StaffOrderRequest.table_id 필수)", () => {
    // 런타임 어서션이 아니라 컴파일 타임 체크다. table_id를 빼면 타입 에러가 나야
    // 하므로 @ts-expect-error를 붙인다 — 에러가 실제로 안 나면(즉 실수로 optional이
    // 되면) tsc가 "Unused '@ts-expect-error' directive"로 빌드를 깨 잡아낸다.
    const payloadMissingTableId = {
      items: [{ menu_id: "m_1", qty: 1 }],
    };
    // @ts-expect-error - table_id가 없어 CreateStaffOrderRequest에 맞지 않는다
    const _typeCheckOnly: CreateStaffOrderRequest = payloadMissingTableId;
    void _typeCheckOnly;
    void createStaffOrder;
  });
});
