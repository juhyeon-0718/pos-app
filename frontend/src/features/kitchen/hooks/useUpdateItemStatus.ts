import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateKitchenItemStatus, type ItemStatus } from "../../../api/kitchen";
import { useAuthStore } from "../../../hooks/useAuthStore";

export function useUpdateItemStatus() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();

  return useMutation<void, Error, { itemId: string; status: ItemStatus }>({
    mutationFn: ({ itemId, status }) => {
      if (!accessToken) throw new Error("NO_ACCESS_TOKEN");
      return updateKitchenItemStatus(accessToken, itemId, status);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["kitchen", "queue"] });
    },
  });
}
