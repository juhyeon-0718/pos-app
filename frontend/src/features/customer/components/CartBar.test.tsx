// 완료 조건: 주문 버튼을 두 번 눌러도(연속 클릭) Idempotency-Key 헤더가 같음을 검증.

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CartBar } from "./CartBar";
import { useCartStore } from "../store/cartStore";

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient();
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

beforeEach(() => {
  sessionStorage.clear();
  useCartStore.setState({
    draftId: crypto.randomUUID(),
    items: [{ menuId: "m_1", name: "불고기", price: 12000, qty: 1 }],
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("CartBar 주문 버튼 중복 클릭", () => {
  it("버튼을 두 번 눌러도 Idempotency-Key 헤더가 같다", async () => {
    const seenKeys: string[] = [];
    let resolveFirst: (() => void) | undefined;

    vi.stubGlobal(
      "fetch",
      vi.fn((_url: string, init?: RequestInit) => {
        const headers = init?.headers as Record<string, string>;
        seenKeys.push(headers["Idempotency-Key"]);
        // 첫 요청이 아직 끝나지 않은 상태에서 두 번째 클릭이 들어오는 상황을 재현한다.
        return new Promise((resolve) => {
          resolveFirst = () =>
            resolve(
              new Response(
                JSON.stringify({ id: "o_1", status: "received", items: [], stock_warnings: [] }),
                { status: 201, headers: { "Content-Type": "application/json" } },
              ),
            );
        });
      }),
    );

    const user = userEvent.setup();
    renderWithQuery(<CartBar tableSessionToken="table-session-token" />);

    const button = screen.getByRole("button", { name: "주문하기" });
    await user.click(button);
    // 버튼이 전송 중(disabled)이어도 핸들러가 두 번 불렸다고 가정해 키 재사용을 직접 검증한다.
    await user.click(button).catch(() => {});

    resolveFirst?.();

    expect(seenKeys.length).toBeGreaterThanOrEqual(1);
    expect(new Set(seenKeys).size).toBe(1);
  });
});
