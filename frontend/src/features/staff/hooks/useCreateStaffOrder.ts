import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createStaffOrder, type CreateStaffOrderRequest, type Order } from "../../../api/orders";
import { useAuthStore } from "../../../hooks/useAuthStore";
import { useStaffOrderFormStore } from "../store/staffOrderFormStore";

export function useCreateStaffOrder() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const draftId = useStaffOrderFormStore((s) => s.draftId);
  const tableId = useStaffOrderFormStore((s) => s.tableId);
  const items = useStaffOrderFormStore((s) => s.items);
  const clear = useStaffOrderFormStore((s) => s.clear);
  const queryClient = useQueryClient();

  return useMutation<Order, Error, void>({
    mutationFn: () => {
      if (!accessToken) throw new Error("NO_ACCESS_TOKEN");
      if (!tableId) throw new Error("NO_TABLE_ID");
      const payload: CreateStaffOrderRequest = {
        table_id: tableId,
        items: items.map((it) => ({ menu_id: it.menuId, qty: it.qty })),
      };
      return createStaffOrder(draftId, accessToken, payload);
    },
    onSuccess: () => {
      clear();
      queryClient.invalidateQueries({ queryKey: ["orders", "all"] });
    },
  });
}
