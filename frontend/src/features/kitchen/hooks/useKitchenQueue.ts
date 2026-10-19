// 주방 화면: GET /kitchen/queue 5초 폴링(D-23: SSE는 추후, 지금은 폴링으로 시작).
// TODO(F-05 이후): 백엔드 SSE 붙으면 staff/kitchen/owner 화면은 SSE로 전환 검토.

import { useQuery } from "@tanstack/react-query";
import { fetchKitchenQueue, type OrderItem } from "../../../api/kitchen";
import { useAuthStore } from "../../../hooks/useAuthStore";

const POLL_INTERVAL_MS = 5_000;

export function useKitchenQueue() {
  const accessToken = useAuthStore((s) => s.accessToken);

  return useQuery<OrderItem[]>({
    queryKey: ["kitchen", "queue"],
    queryFn: () => fetchKitchenQueue(accessToken as string),
    enabled: Boolean(accessToken),
    refetchInterval: POLL_INTERVAL_MS,
    refetchIntervalInBackground: true,
  });
}
