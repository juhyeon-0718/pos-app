// 장바구니 -> POST /orders 제출. draftId는 cartStore가 들고 있는 현재 장바구니의
// 제출 시도 식별자다. 성공 시에만 cartStore.clear()로 장바구니를 비우고 새 draftId를 받는다
// — 실패 시에는 draftId를 유지해 재시도가 같은 Idempotency-Key를 쓰게 한다 (D-15).

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createOrder, type CreateOrderRequestItem, type Order } from "../../../api/orders";
import { useCartStore } from "../store/cartStore";

export function useCreateOrder(tableSessionToken: string | null) {
  const queryClient = useQueryClient();
  const draftId = useCartStore((s) => s.draftId);
  const items = useCartStore((s) => s.items);
  const clear = useCartStore((s) => s.clear);

  return useMutation<Order, Error, void>({
    mutationFn: () => {
      if (!tableSessionToken) throw new Error("NO_TABLE_SESSION");
      const payload: { items: CreateOrderRequestItem[] } = {
        items: items.map((it) => ({ menu_id: it.menuId, qty: it.qty })),
      };
      return createOrder(draftId, tableSessionToken, payload);
    },
    onSuccess: (order) => {
      clear();
      queryClient.setQueryData<Order[]>(
        ["orders", "mine", tableSessionToken],
        (prev) => (prev ? [order, ...prev] : [order]),
      );
      queryClient.invalidateQueries({ queryKey: ["orders", "mine", tableSessionToken] });
    },
  });
}
