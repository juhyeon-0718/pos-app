// 직원 대리 주문 입력 상태 (Zustand). customer의 cartStore와 패턴은 같지만
// table_id가 필수라는 점이 달라 별도 스토어로 둔다(feature 간 import 금지, D-25).
// draftId: 이 주문 시도의 Idempotency-Key 식별자. 제출 성공 시에만 새로 발급한다.

import { create } from "zustand";

export interface StaffOrderItem {
  menuId: string;
  name: string;
  price: number;
  qty: number;
}

interface StaffOrderFormState {
  draftId: string;
  tableId: string;
  items: StaffOrderItem[];
  setTableId: (tableId: string) => void;
  addItem: (menu: { id: string; name: string; price: number }) => void;
  setQty: (menuId: string, qty: number) => void;
  clear: () => void;
}

function newDraftId(): string {
  return crypto.randomUUID();
}

export const useStaffOrderFormStore = create<StaffOrderFormState>((set) => ({
  draftId: newDraftId(),
  tableId: "",
  items: [],
  setTableId: (tableId) => set({ tableId }),
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
  setQty: (menuId, qty) =>
    set((state) => ({
      items:
        qty <= 0
          ? state.items.filter((it) => it.menuId !== menuId)
          : state.items.map((it) => (it.menuId === menuId ? { ...it, qty } : it)),
    })),
  clear: () => set({ items: [], tableId: "", draftId: newDraftId() }),
}));
