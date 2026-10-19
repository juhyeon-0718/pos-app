// GET /menus: 메뉴 목록 (손님/직원/주방/사장 공통). 손님 화면은 tableToken 인증으로 호출.
// B-03(D-30 계약 보강)부터 응답이 MenuListResponse(items/next_cursor/has_more)로 바뀌었다.
// 손님 메뉴판은 메뉴 수가 적어 1페이지로 충분하므로 커서 추가 요청은 하지 않고 items만 쓴다.

import type { components } from "./schema";
import { authorizedFetch } from "./httpClient";

export type Menu = components["schemas"]["Menu"];

const BASE_URL = "/api/v1";

export async function fetchMenus(
  tableSessionToken: string,
  baseUrl = BASE_URL,
): Promise<Menu[]> {
  const res = await fetch(`${baseUrl}/menus`, {
    headers: { "X-Table-Session-Token": tableSessionToken },
  });
  if (!res.ok) {
    throw new Error(`FETCH_MENUS_FAILED: ${res.status}`);
  }
  const body: components["schemas"]["MenuListResponse"] = await res.json();
  return body.items ?? [];
}

// 직원 대리 주문(F-05): bearerAuth로 같은 /menus를 호출한다(계약상 tableToken·bearerAuth 둘 다 허용).
// 토큰 만료 시 authorizedFetch가 로그아웃시킨다.
export async function fetchMenusAsStaff(
  accessToken: string,
  baseUrl = BASE_URL,
): Promise<Menu[]> {
  const res = await authorizedFetch(`${baseUrl}/menus`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!res.ok) {
    throw new Error(`FETCH_MENUS_FAILED: ${res.status}`);
  }
  const body: components["schemas"]["MenuListResponse"] = await res.json();
  return body.items ?? [];
}
