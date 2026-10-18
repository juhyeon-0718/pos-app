// 완료 조건: GET /kitchen/queue 5초 폴링 간격 검증.

import { renderHook } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useKitchenQueue } from "./useKitchenQueue";
import { useAuthStore } from "../../../shared/auth/authStore";

function wrapper({ children }: { children: ReactNode }) {
  const queryClient = new QueryClient();
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

beforeEach(() => {
  sessionStorage.clear();
  useAuthStore.setState({ accessToken: "staff-token", role: "kitchen" });
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.useRealTimers();
});

describe("useKitchenQueue 5초 폴링", () => {
  it("5초마다 큐를 다시 불러온다", async () => {
    vi.useFakeTimers();
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify([]), { status: 200, headers: { "Content-Type": "application/json" } }),
    );
    vi.stubGlobal("fetch", fetchMock);

    renderHook(() => useKitchenQueue(), { wrapper });

    await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));

    await vi.advanceTimersByTimeAsync(5_000);
    await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));

    await vi.advanceTimersByTimeAsync(5_000);
    await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
  });
});
