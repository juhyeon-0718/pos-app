// 사장 화면 공용 호출 래퍼: bearerAuth 헤더, 401 로그아웃, 409·422를 ApiError로 변환한다.

import type { components } from "./schema";
import { authorizedFetch } from "./httpClient";

export type ApiErrorBody = components["schemas"]["Error"];

export class ApiError extends Error {
  status: number;
  code: string | null;
  detail: string | null;
  constructor(status: number, code: string | null, detail: string | null) {
    super(`API_ERROR: ${status}${code ? ` ${code}` : ""}`);
    this.status = status;
    this.code = code;
    this.detail = detail;
  }
}

export const BASE_URL = "/api/v1";

export async function ownerFetch<T>(
  accessToken: string,
  path: string,
  init: { method?: string; body?: unknown } = {},
  baseUrl = BASE_URL,
): Promise<T> {
  const headers: Record<string, string> = { Authorization: `Bearer ${accessToken}` };
  if (init.body !== undefined) headers["Content-Type"] = "application/json";
  const res = await authorizedFetch(`${baseUrl}${path}`, {
    method: init.method ?? "GET",
    headers,
    body: init.body === undefined ? undefined : JSON.stringify(init.body),
  });
  if (!res.ok) {
    let code: string | null = null;
    let detail: string | null = null;
    try {
      const body = await res.json();
      // 계약은 {code, detail}이지만 FastAPI는 detail 안에 한 겹 감싸거나(객체),
      // 422 검증 오류는 detail을 배열로 준다. 세 형태 모두 문자열로 정리한다.
      const inner = body?.detail && typeof body.detail === "object" && !Array.isArray(body.detail) ? body.detail : body;
      if (typeof inner?.code === "string") code = inner.code;
      if (typeof inner?.detail === "string") detail = inner.detail;
      else if (Array.isArray(body?.detail)) detail = body.detail.map((d: { msg?: string }) => d?.msg).filter(Boolean).join(", ") || null;
    } catch {
      // 본문 없는 오류(403 등)는 상태 코드만 쓴다.
    }
    throw new ApiError(res.status, code, detail);
  }
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}
