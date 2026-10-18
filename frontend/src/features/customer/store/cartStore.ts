// 손님 장바구니 로컬 상태 (Zustand). 서버 데이터가 아니므로 React Query 대상이 아니다.
// draftId: 현재 장바구니 "제출 시도" 식별자. 주문을 비우고 새로 담을 때만 새로 발급한다 —
// 같은 draftId로 재시도(버튼 중복 클릭/네트워크 재시도)해야 api/orders.ts가 같은
// Idempotency-Key를 재사용한다 (D-15).

import { create } from "zustand";

export interface CartItem {
  menuId: string;
  name: string;
  price: number;
  qty: number;
}

interface CartState {
  draftId: string;
  items: CartItem[];
  addItem: (menu: { id: string; name: string; price: number }) => void;
  removeItem: (menuId: string) => void;
  setQty: (menuId: string, qty: number) => void;
  clear: () => void;
  totalAmount: () => number;
}

function newDraftId(): string {
  return crypto.randomUUID();
}

export const useCartStore = create<CartState>((set, get) => ({
  draftId: newDraftId(),
  items: [],
  addItem: (menu) =>
    set((state) => {
      const existing = state.items.find((it) => it.menuId === menu.id);
      if (existing) {
        return {
          items: state.items.map((it) =>
            it.menuId === menu.id ? { ...it, qty: it.qty + 1 } : it,
          ),
        };
      }
      return {
        items: [...state.items, { menuId: menu.id, name: menu.name, price: menu.price, qty: 1 }],
      };
    }),
  removeItem: (menuId) =>
    set((state) => ({ items: state.items.filter((it) => it.menuId !== menuId) })),
  setQty: (menuId, qty) =>
    set((state) => ({
      items:
        qty <= 0
          ? state.items.filter((it) => it.menuId !== menuId)
          : state.items.map((it) => (it.menuId === menuId ? { ...it, qty } : it)),
    })),
  // 주문 제출 성공/완료 후에만 호출한다 — draftId를 새로 발급해 다음 장바구니가
  // 새 Idempotency-Key를 쓰도록 한다.
  clear: () => set({ items: [], draftId: newDraftId() }),
  totalAmount: () => get().items.reduce((sum, it) => sum + it.price * it.qty, 0),
}));
