// 직원 대리 주문 폼. table_id는 필수 입력이다(계약: StaffOrderRequest.table_id).

import { useStaffMenus } from "../hooks/useStaffMenus";
import { useCreateStaffOrder } from "../hooks/useCreateStaffOrder";
import { useStaffOrderFormStore } from "../store/staffOrderFormStore";

export function StaffNewOrderForm() {
  const menus = useStaffMenus();
  const tableId = useStaffOrderFormStore((s) => s.tableId);
  const setTableId = useStaffOrderFormStore((s) => s.setTableId);
  const items = useStaffOrderFormStore((s) => s.items);
  const addItem = useStaffOrderFormStore((s) => s.addItem);
  const setQty = useStaffOrderFormStore((s) => s.setQty);
  const createStaffOrder = useCreateStaffOrder();

  const canSubmit = Boolean(tableId) && items.length > 0 && !createStaffOrder.isPending;

  return (
    <section className="staff-new-order">
      <h2>대리 주문</h2>
      <label className="staff-table-input">
        테이블 번호
        <input
          type="text"
          value={tableId}
          onChange={(e) => setTableId(e.target.value)}
          placeholder="예: t_5"
          required
        />
      </label>

      {menus.data && (
        <ul className="staff-menu-list">
          {menus.data
            .filter((m) => m.is_active !== false)
            .map((menu) => (
              <li key={menu.id} className="staff-menu-row">
                <span>{menu.name}</span>
                <button
                  type="button"
                  onClick={() =>
                    addItem({ id: menu.id ?? "", name: menu.name ?? "", price: menu.price ?? 0 })
                  }
                >
                  담기
                </button>
              </li>
            ))}
        </ul>
      )}

      {items.length > 0 && (
        <ul className="staff-cart-items">
          {items.map((item) => (
            <li key={item.menuId}>
              {item.name} x
              <input
                type="number"
                min={0}
                value={item.qty}
                onChange={(e) => setQty(item.menuId, Number(e.target.value))}
              />
            </li>
          ))}
        </ul>
      )}

      <button
        type="button"
        className="staff-submit-btn"
        disabled={!canSubmit}
        onClick={() => createStaffOrder.mutate()}
      >
        {createStaffOrder.isPending ? "주문 중..." : "대리 주문 등록"}
      </button>
      {createStaffOrder.isError && (
        <p className="staff-order-error" role="alert">
          주문 등록에 실패했습니다.
        </p>
      )}
    </section>
  );
}
