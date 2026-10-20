// F-06: owner 역할 제한, 빈 상태, 409 오류 표시.
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { OwnerPage } from "./OwnerPage";
import { useAuthStore } from "../../hooks/useAuthStore";

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
const list = (items: unknown[]) => json({ items, next_cursor: null, has_more: false });

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <OwnerPage />
    </QueryClientProvider>,
  );
}

beforeEach(() => sessionStorage.clear());
afterEach(() => vi.unstubAllGlobals());

describe("OwnerPage", () => {
  it("staff 역할은 접근할 수 없고 API를 호출하지 않는다", () => {
    useAuthStore.setState({ accessToken: "t", role: "staff" });
    const f = vi.fn();
    vi.stubGlobal("fetch", f);
    renderPage();
    expect(screen.getByRole("alert")).toHaveTextContent("사장 계정");
    expect(f).not.toHaveBeenCalled();
  });

  it("메뉴가 없으면 빈 상태 문구를 보여 준다", async () => {
    useAuthStore.setState({ accessToken: "t", role: "owner" });
    vi.stubGlobal("fetch", vi.fn(async () => list([])));
    renderPage();
    expect(await screen.findByText(/등록된 메뉴가 없습니다/)).toBeInTheDocument();
  });

  it("식재료 비활성화 409 detail을 화면에 보여 준다", async () => {
    useAuthStore.setState({ accessToken: "t", role: "owner" });
    vi.stubGlobal("confirm", () => true);
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string, init?: RequestInit) => {
        if (init?.method === "DELETE") return json({ code: "IN_USE", detail: "레시피에서 사용 중입니다" }, 409);
        if (url.endsWith("/ingredients")) return list([{ id: "i1", name: "양파", unit: "kg", current_stock: 3 }]);
        return list([]);
      }),
    );
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "식재료" }));
    await userEvent.click(await screen.findByRole("button", { name: "비활성화" }));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("레시피에서 사용 중입니다"));
  });
});
