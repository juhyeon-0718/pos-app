import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateOrderStatus } from "../../../api/orders";
import { useAuthStore } from "../../../hooks/useAuthStore";
import type { OrderStatus } from "../../../constants/status";

export function useUpdateOrderStatus() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();

  return useMutation<void, Error, { orderId: string; status: OrderStatus }>({
    mutationFn: async ({ orderId, status }) => {
      if (!accessToken) throw new Error("NO_ACCESS_TOKEN");
      await updateOrderStatus(accessToken, orderId, status);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders", "all"] });
    },
  });
}
