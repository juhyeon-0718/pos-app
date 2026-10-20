// F-07: owner 역할 제한, 빈 상태, 오류 배너, 일시품절·삭제·판매 다시 시작·사용중지 동작.
import { render, screen, waitFor, within } from "@testing-library/react";
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

const menu = (over: object = {}) => ({ id: "m1", name: "김치찌개", price: 8000, category: "찌개", is_active: true, ...over });

beforeEach(() => {
  sessionStorage.clear();
  useAuthStore.setState({ accessToken: "t", role: "owner" });
  vi.stubGlobal("confirm", () => true);
});
afterEach(() => vi.unstubAllGlobals());

describe("OwnerPage", () => {
  it("staff 역할은 접근할 수 없고 API를 호출하지 않는다", () => {
    useAuthStore.setState({ accessToken: "t", role: "staff" });
    const f = vi.fn();
    vi.stubGlobal("fetch", f);
    renderPage();
    expect(screen.getByRole("alert")).toHaveTextContent("사장 계정만 관리할 수 있어요.");
    expect(f).not.toHaveBeenCalled();
  });

  it("메뉴가 없으면 빈 상태 문구를 보여 준다", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => list([])));
    renderPage();
    expect(await screen.findByText("아직 등록한 메뉴가 없어요")).toBeInTheDocument();
  });

  it("식재료 빈 상태에는 레시피·재고 차감 문구가 없다(D-34)", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => list([])));
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "식재료 관리" }));
    expect(await screen.findByText("아직 등록한 식재료가 없어요")).toBeInTheDocument();
    expect(screen.queryByText(/레시피|자동으로 줄어/)).not.toBeInTheDocument();
  });

  it("목록 조회 실패는 배너와 다시 시도 버튼을 보여 준다", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ code: "X", detail: "x" }, 500)));
    renderPage();
    expect(await screen.findByText(/메뉴 목록을 불러오지 못했어요/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "다시 시도" })).toBeInTheDocument();
  });

  it("메뉴 저장 409는 명세 문구와 서버 detail을 배너로 보여 준다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_u: string, init?: RequestInit) =>
        init?.method === "POST" ? json({ code: "DUP", detail: "이미 있는 이름" }, 409) : list([]),
      ),
    );
    renderPage();
    await userEvent.type(await screen.findByLabelText(/메뉴 이름/), "된장찌개");
    await userEvent.type(screen.getByLabelText(/가격/), "9000");
    await userEvent.click(screen.getByRole("button", { name: "메뉴 추가" }));
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("같은 이름의 메뉴가 이미 있어요.");
    expect(alert).toHaveTextContent("이미 있는 이름");
  });

  it("활성 메뉴를 '일시품절'로 바꾸면 PATCH로 is_active=false를 보낸다", async () => {
    const f = vi.fn(async (_u: string, init?: RequestInit) =>
      init?.method === "PATCH" ? json(menu({ is_active: false })) : list([menu()]),
    );
    vi.stubGlobal("fetch", f);
    renderPage();
    await userEvent.click(await screen.findByRole("button", { name: "김치찌개 일시품절" }));
    await waitFor(() => {
      const c = f.mock.calls.find((x) => x[1]?.method === "PATCH");
      expect(c).toBeTruthy();
      expect(JSON.parse(c![1]!.body as string)).toMatchObject({ name: "김치찌개", price: 8000, is_active: false });
    });
  });

  it("일시품절 메뉴는 배지와 '판매 다시 시작'을 보여 주고 PATCH로 is_active=true를 보낸다", async () => {
    const f = vi.fn(async (_u: string, init?: RequestInit) =>
      init?.method === "PATCH" ? json(menu()) : list([menu({ is_active: false })]),
    );
    vi.stubGlobal("fetch", f);
    renderPage();
    expect(await screen.findByText("⊘ 일시품절")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "김치찌개 일시품절" })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "김치찌개 판매 다시 시작" }));
    await waitFor(() => {
      const c = f.mock.calls.find((x) => x[1]?.method === "PATCH");
      expect(JSON.parse(c![1]!.body as string).is_active).toBe(true);
    });
  });

  it("메뉴 '삭제'는 DELETE를 호출한다", async () => {
    const f = vi.fn(async (_u: string, init?: RequestInit) =>
      init?.method === "DELETE" ? new Response(null, { status: 204 }) : list([menu()]),
    );
    vi.stubGlobal("fetch", f);
    renderPage();
    await userEvent.click(await screen.findByRole("button", { name: "김치찌개 삭제" }));
    await waitFor(() => expect(f.mock.calls.some((x) => x[1]?.method === "DELETE" && x[0] === "/api/v1/menus/m1")).toBe(true));
  });

  it("수정 폼의 '일시품절' 체크박스로 상태를 바꿔 저장한다", async () => {
    const f = vi.fn(async (_u: string, init?: RequestInit) =>
      init?.method === "PATCH" ? json(menu({ is_active: true })) : list([menu({ is_active: false })]),
    );
    vi.stubGlobal("fetch", f);
    renderPage();
    await userEvent.click(await screen.findByRole("button", { name: "김치찌개 수정" }));
    const box = screen.getByRole("checkbox", { name: /일시품절/ });
    expect(box).toBeChecked();
    await userEvent.click(box);
    await userEvent.click(screen.getByRole("button", { name: "저장" }));
    await waitFor(() => {
      const c = f.mock.calls.find((x) => x[1]?.method === "PATCH");
      expect(JSON.parse(c![1]!.body as string).is_active).toBe(true);
    });
  });

  it("식재료 사용중지 409를 명세 문구로 보여 준다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string, init?: RequestInit) => {
        if (init?.method === "DELETE") return json({ code: "IN_USE", detail: "사용 중입니다" }, 409);
        if (url.endsWith("/ingredients")) return list([{ id: "i1", name: "양파", unit: "kg", current_stock: 3 }]);
        return list([]);
      }),
    );
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "식재료 관리" }));
    await userEvent.click(await screen.findByRole("button", { name: "양파 사용중지" }));
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("사용중지로 바꿀 수 없어요");
    expect(alert).toHaveTextContent("사용 중입니다");
  });

  it("is_active=false 식재료는 '사용중지'로 표시하고 사용중지 버튼을 숨긴다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) =>
        url.endsWith("/ingredients")
          ? list([{ id: "i1", name: "양파", unit: "kg", current_stock: 3, is_active: false }])
          : list([]),
      ),
    );
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "식재료 관리" }));
    const row = (await screen.findByText("양파")).closest("li")!;
    expect(within(row).getByText("⊘ 사용중지")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "양파 사용중지" })).not.toBeInTheDocument();
  });
});
