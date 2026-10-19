// 직원 화면: GET /orders 5초 폴링 (D-23: 직원 화면은 SSE 유지 방향이나 MVP는 폴링으로 시작).
// TODO(이후): 백엔드 SSE 붙으면 전환 검토.

import { useQuery } from "@tanstack/react-query";
import { fetchAllOrders, type Order } from "../../../api/orders";
import { useAuthStore } from "../../../hooks/useAuthStore";
import type { OrderStatus } from "../../../constants/status";

const POLL_INTERVAL_MS = 5_000;

export function useAllOrders(status?: OrderStatus) {
  const accessToken = useAuthStore((s) => s.accessToken);

  return useQuery<Order[]>({
    queryKey: ["orders", "all", status ?? "ALL"],
    queryFn: () => fetchAllOrders(accessToken as string, status),
    enabled: Boolean(accessToken),
    refetchInterval: POLL_INTERVAL_MS,
    refetchIntervalInBackground: true,
  });
}
