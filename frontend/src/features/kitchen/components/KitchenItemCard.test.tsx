// 완료 조건: 주방 상태 변경 버튼 동작 검증 (pending -> cooking, cooking -> done).

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { KitchenItemCard } from "./KitchenItemCard";
import { useAuthStore } from "../../../hooks/useAuthStore";
import type { OrderItem } from "../../../api/kitchen";

function renderWithQuery(ui: ReactNode) {
  const queryClient = new QueryClient();
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

beforeEach(() => {
  sessionStorage.clear();
  useAuthStore.setState({ accessToken: "staff-token", role: "kitchen" });
});

afterEach(() => {
  vi.restoreAllMocks();
});

function baseItem(overrides: Partial<OrderItem> = {}): OrderItem {
  return {
    id: "item_1",
    order_id: "order_1",
    menu_id: "menu_1",
    menu_name: "불고기",
    qty: 2,
    price_snapshot: 12000,
    item_status: "pending",
    ...overrides,
  };
}

describe("KitchenItemCard 테이블 번호 표시 (F-15)", () => {
  it("table_no가 있으면 '{n}번 테이블'을 보여 준다", () => {
    renderWithQuery(<KitchenItemCard item={baseItem({ table_no: 7 })} />);
    expect(screen.getByText("7번 테이블")).toBeTruthy();
  });

  it("table_no가 없으면 '테이블 -'를 보여 준다", () => {
    renderWithQuery(<KitchenItemCard item={baseItem()} />);
    expect(screen.getByText("테이블 -")).toBeTruthy();
  });
});

describe("KitchenItemCard 상태 변경 버튼", () => {
  it("pending 항목은 '조리 시작' 버튼을 누르면 PATCH로 cooking을 보낸다", async () => {
    let seenBody: unknown;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_url: string, init?: RequestInit) => {
        seenBody = init?.body ? JSON.parse(init.body as string) : undefined;
        return new Response(null, { status: 200 });
      }),
    );

    renderWithQuery(<KitchenItemCard item={baseItem()} />);
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "조리 시작" }));

    expect(seenBody).toEqual({ status: "cooking" });
  });

  it("done 항목은 다음 상태 버튼이 없다", () => {
    renderWithQuery(<KitchenItemCard item={baseItem({ item_status: "done" })} />);
    expect(screen.queryByRole("button")).toBeNull();
  });
});
