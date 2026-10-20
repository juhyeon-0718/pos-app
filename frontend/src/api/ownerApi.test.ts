// F-06: 메뉴·식재료·레시피 API 호출 형식(메서드·경로·헤더·본문)과 409/422 오류 변환 검증.
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createMenu, deleteMenu, listMenusAsOwner } from "./menus";
import { deactivateIngredient, listIngredients } from "./ingredients";
import { ApiError } from "./ownerFetch";

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

beforeEach(() => sessionStorage.clear());
afterEach(() => vi.unstubAllGlobals());

describe("사장 API", () => {
  it("메뉴 목록은 items만 꺼내고 Bearer 헤더를 보낸다", async () => {
    const f = vi.fn(async () => json({ items: [{ id: "m1", name: "김치찌개" }], next_cursor: null, has_more: false }));
    vi.stubGlobal("fetch", f);
    const menus = await listMenusAsOwner("tok");
    expect(menus).toHaveLength(1);
    const [url, init] = f.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/api/v1/menus");
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer tok");
  });

  it("메뉴 생성은 POST, 삭제는 DELETE(204)", async () => {
    const f = vi.fn(async (_u: string, init?: RequestInit) =>
      init?.method === "DELETE" ? new Response(null, { status: 204 }) : json({ id: "m2" }, 201),
    );
    vi.stubGlobal("fetch", f);
    await createMenu("tok", { name: "비빔밥", price: 9000, is_active: true });
    await expect(deleteMenu("tok", "m2")).resolves.toBeUndefined();
    expect(f.mock.calls[0][1]?.method).toBe("POST");
    expect(f.mock.calls[0][1]?.body).toBe(JSON.stringify({ name: "비빔밥", price: 9000, is_active: true }));
    expect(f.mock.calls[1][0]).toBe("/api/v1/menus/m2");
  });

  it("식재료 비활성화 409는 ApiError(code, detail)로 던진다", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ code: "INGREDIENT_IN_USE", detail: "레시피에서 사용 중" }, 409)));
    const err = await deactivateIngredient("tok", "i1").catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(409);
    expect(err.detail).toBe("레시피에서 사용 중");
  });

  it("422도 ApiError, 401은 로그아웃", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ code: "VALIDATION", detail: "이름 필수" }, 422)));
    await expect(listIngredients("tok")).rejects.toMatchObject({ status: 422 });
    const { useAuthStore } = await import("../hooks/useAuthStore");
    useAuthStore.setState({ accessToken: "tok", role: "owner" });
    vi.stubGlobal("fetch", vi.fn(async () => new Response(null, { status: 401 })));
    await expect(listIngredients("tok")).rejects.toMatchObject({ status: 401 });
    expect(useAuthStore.getState().accessToken).toBeNull();
  });
});
