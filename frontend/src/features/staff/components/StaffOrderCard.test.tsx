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

describe("StaffOrderCard 테이블 번호 표시 (F-15)", () => {
  it("table_no가 있으면 '{n}번 테이블'을 보여 주고 table_id는 보이지 않는다", () => {
    renderWithQuery(<StaffOrderCard order={baseOrder({ table_no: 3 })} />);
    expect(screen.getByText("3번 테이블")).toBeTruthy();
    expect(screen.queryByText(/t_5/)).toBeNull();
  });

  it("table_no가 없으면 '테이블 -'를 보여 준다", () => {
    renderWithQuery(<StaffOrderCard order={baseOrder()} />);
    expect(screen.getByText("테이블 -")).toBeTruthy();
  });

  it("table_no가 명시적 null이어도 '테이블 -'를 보여 준다 (서버가 null을 내려 주는 경우)", () => {
    // 계약 타입은 number지만 서버는 null을 줄 수 있어 타입을 우회해 검증한다.
    renderWithQuery(<StaffOrderCard order={baseOrder({ table_no: null as unknown as number })} />);
    expect(screen.getByText("테이블 -")).toBeTruthy();
    expect(screen.queryByText(/null/)).toBeNull();
  });
});

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

  it("항목별 조리 상태(대기/조리중/완료)가 라벨로 보인다", () => {
    renderWithQuery(
      <StaffOrderCard
        order={baseOrder({
          status: "received",
          items: [
            { id: "item_1", menu_name: "불고기", qty: 1, item_status: "pending" },
            { id: "item_2", menu_name: "비빔밥", qty: 1, item_status: "done" },
          ],
        })}
      />,
    );
    expect(screen.getByText("대기")).toBeTruthy();
    expect(screen.getByText("완료")).toBeTruthy();
  });

  it("D-32: 항목이 전부 done이 아니면 '서빙완료로 변경' 버튼이 비활성이다", () => {
    renderWithQuery(
      <StaffOrderCard
        order={baseOrder({
          status: "cooking",
          items: [
            { id: "item_1", menu_name: "불고기", qty: 1, item_status: "done" },
            { id: "item_2", menu_name: "비빔밥", qty: 1, item_status: "cooking" },
          ],
        })}
      />,
    );
    expect(screen.getByRole("button", { name: "서빙완료로 변경" })).toBeDisabled();
  });

  it("D-32: 항목이 전부 done이면 '서빙완료로 변경' 버튼이 활성화되고 클릭하면 status=served를 보낸다", async () => {
    let seenBody: unknown;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_url: string, init?: RequestInit) => {
        seenBody = init?.body ? JSON.parse(init.body as string) : undefined;
        return new Response(JSON.stringify({}), { status: 200 });
      }),
    );

    renderWithQuery(
      <StaffOrderCard
        order={baseOrder({
          status: "cooking",
          items: [
            { id: "item_1", menu_name: "불고기", qty: 1, item_status: "done" },
            { id: "item_2", menu_name: "비빔밥", qty: 1, item_status: "done" },
          ],
        })}
      />,
    );

    const button = screen.getByRole("button", { name: "서빙완료로 변경" });
    expect(button).not.toBeDisabled();

    const user = userEvent.setup();
    await user.click(button);
    expect(seenBody).toEqual({ status: "served" });
  });
});
