// 완료 조건: 대리 주문 등록 버튼을 두 번 눌러도 Idempotency-Key가 같음을 검증.
// table_id가 없으면 제출 버튼이 비활성화되는 것도 함께 확인한다.

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { StaffNewOrderForm } from "./StaffNewOrderForm";
import { useAuthStore } from "../../../hooks/useAuthStore";
import { useStaffOrderFormStore } from "../store/staffOrderFormStore";

function renderWithQuery(ui: ReactNode) {
  const queryClient = new QueryClient();
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

beforeEach(() => {
  sessionStorage.clear();
  useAuthStore.setState({ accessToken: "staff-token", role: "staff" });
  useStaffOrderFormStore.setState({
    draftId: crypto.randomUUID(),
    tableId: "",
    items: [],
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("StaffNewOrderForm", () => {
  it("table_id가 비어 있으면 제출 버튼이 비활성화된다", () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("[]", { status: 200 })));
    useStaffOrderFormStore.setState({
      items: [{ menuId: "m_1", name: "불고기", price: 12000, qty: 1 }],
    });

    renderWithQuery(<StaffNewOrderForm />);
    expect(screen.getByRole("button", { name: "대리 주문 등록" })).toBeDisabled();
  });

  it("등록 버튼을 두 번 눌러도 Idempotency-Key 헤더가 같다", async () => {
    useStaffOrderFormStore.setState({
      tableId: "t_5",
      items: [{ menuId: "m_1", name: "불고기", price: 12000, qty: 1 }],
    });

    const seenKeys: string[] = [];
    let resolveFirst: (() => void) | undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string, init?: RequestInit) => {
        if (url.includes("/menus")) {
          return Promise.resolve(
            new Response(JSON.stringify({ items: [] }), { status: 200 }),
          );
        }
        const headers = init?.headers as Record<string, string>;
        seenKeys.push(headers["Idempotency-Key"]);
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

    renderWithQuery(<StaffNewOrderForm />);
    const user = userEvent.setup();
    const button = screen.getByRole("button", { name: "대리 주문 등록" });

    await user.click(button);
    await user.click(button).catch(() => {});
    resolveFirst?.();

    expect(seenKeys.length).toBeGreaterThanOrEqual(1);
    expect(new Set(seenKeys).size).toBe(1);
  });
});
