// 완료 조건: 상태별로 허용된 동작 버튼만 노출되는지, 클릭 시 올바른 status가 전송되는지 검증.

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { StaffOrderCard } from "./StaffOrderCard";
import { useAuthStore } from "../../../hooks/useAuthStore";
import type { Order } from "../../../api/orders";

function renderWithQuery(ui: ReactNode) {
  const queryClient = new QueryClient();
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

beforeEach(() => {
  sessionStorage.clear();
  useAuthStore.setState({ accessToken: "staff-token", role: "staff" });
});

afterEach(() => {
  vi.restoreAllMocks();
});

function baseOrder(overrides: Partial<Order> = {}): Order {
  return {
    id: "order_1",
    table_id: "t_5",
    status: "received",
    total_amount: 12000,
    items: [{ id: "item_1", menu_name: "불고기", qty: 1 }],
    stock_warnings: [],
    ...overrides,
  };
}

describe("StaffOrderCard 상태별 동작 버튼", () => {
  it("received 상태는 '조리 전 취소' 버튼만 있고 클릭하면 status=cancelled를 보낸다", async () => {
    let seenBody: unknown;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_url: string, init?: RequestInit) => {
        seenBody = init?.body ? JSON.parse(init.body as string) : undefined;
        return new Response(JSON.stringify({}), { status: 200 });
      }),
    );

    renderWithQuery(<StaffOrderCard order={baseOrder()} />);
    expect(screen.getByRole("button", { name: "조리 전 취소" })).toBeTruthy();

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "조리 전 취소" }));
    expect(seenBody).toEqual({ status: "cancelled" });
  });

  it("cooking 상태는 '서빙완료로 변경' 버튼만 있다 (취소 버튼 없음)", () => {
    renderWithQuery(<StaffOrderCard order={baseOrder({ status: "cooking" })} />);
    expect(screen.getByRole("button", { name: "서빙완료로 변경" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "조리 전 취소" })).toBeNull();
  });

  it("served 상태는 '결제완료로 변경' 버튼만 있다", () => {
    renderWithQuery(<StaffOrderCard order={baseOrder({ status: "served" })} />);
    expect(screen.getByRole("button", { name: "결제완료로 변경" })).toBeTruthy();
  });

  it("paid 상태는 동작 버튼이 없다", () => {
    renderWithQuery(<StaffOrderCard order={baseOrder({ status: "paid" })} />);
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("stock_warnings가 있으면 손님 화면과 달리 그대로 노출한다", () => {
    renderWithQuery(
      <StaffOrderCard
        order={baseOrder({
          stock_warnings: [
            { ingredient_id: "ing_1", name: "돼지고기", current_stock: 1, required: 3 },
          ],
        })}
      />,
    );
    expect(screen.getByText(/재고 부족: 돼지고기/)).toBeTruthy();
  });
});
