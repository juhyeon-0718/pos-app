// GET /menus: 메뉴 목록 (손님/직원/주방/사장 공통). 손님 화면은 tableToken 인증으로 호출.

import type { components } from "./schema";

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
  return res.json();
}
