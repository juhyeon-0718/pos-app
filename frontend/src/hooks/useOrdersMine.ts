// D-17: 손님 화면은 GET /orders/mine을 10초 간격으로 폴링한다.
// 손님용 SSE는 MVP 이후 검토 (D-17).

import { useQuery } from "@tanstack/react-query";
import { fetchMyOrders, type Order } from "../api/orders";

const POLL_INTERVAL_MS = 10_000;

export function useOrdersMine(tableSessionToken: string) {
  return useQuery<Order[]>({
    queryKey: ["orders", "mine", tableSessionToken],
    queryFn: () => fetchMyOrders(tableSessionToken),
    enabled: Boolean(tableSessionToken),
    refetchInterval: POLL_INTERVAL_MS,
    // 손님이 다른 탭으로 이동해도 주문 상태는 계속 받아야 하므로 포그라운드 제한을 끈다.
    refetchIntervalInBackground: true,
  });
}
