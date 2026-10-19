// 완료 조건: 401 응답을 받으면 authorizedFetch가 즉시 로그아웃시키는지 검증.

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { authorizedFetch } from "./httpClient";
import { useAuthStore } from "../hooks/useAuthStore";

beforeEach(() => {
  sessionStorage.clear();
  useAuthStore.setState({ accessToken: "expired-token", role: "kitchen" });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("authorizedFetch", () => {
  it("401을 받으면 로그아웃(accessToken/role 초기화)한다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(null, { status: 401 })),
    );

    await authorizedFetch("/api/v1/kitchen/queue", {
      headers: { Authorization: "Bearer expired-token" },
    });

    expect(useAuthStore.getState().accessToken).toBeNull();
    expect(useAuthStore.getState().role).toBeNull();
  });

  it("200 응답에는 로그아웃하지 않는다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("[]", { status: 200 })),
    );

    await authorizedFetch("/api/v1/kitchen/queue", {
      headers: { Authorization: "Bearer valid-token" },
    });

    expect(useAuthStore.getState().accessToken).toBe("expired-token");
  });
});
