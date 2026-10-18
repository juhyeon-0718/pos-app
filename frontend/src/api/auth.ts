// POST /auth/login: 직원/주방/사장 로그인 (공용). 이 응답의 access_token은
// Authorization: Bearer 헤더로 쓴다. tableToken(X-Table-Session-Token)과는 별개 체계.

import type { components } from "./schema";

export type Role = components["schemas"]["Role"];

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: Role;
}

const BASE_URL = "/api/v1";

export async function login(
  username: string,
  password: string,
  baseUrl = BASE_URL,
): Promise<LoginResponse> {
  const res = await fetch(`${baseUrl}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    throw new Error(`LOGIN_FAILED: ${res.status}`);
  }
  return res.json();
}
