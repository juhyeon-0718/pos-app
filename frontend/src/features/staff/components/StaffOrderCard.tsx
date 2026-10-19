// 주문 단위 카드. 상태별로 가능한 다음 동작만 버튼으로 노출한다.
// - received: 조리 전 취소(직원 가능). 조리 시작 후 취소는 사장 전용이라 F-05에는 없다(D-19).
// - cooking: 서빙완료로 변경 (D-32: 항목이 모두 done일 때만 눌림 — 서버도 같은 조건을 409로 강제한다)
// - served: 결제완료로 변경
// - paid/cancelled: 동작 없음

import type { Order } from "../../../api/orders";
import { orderStatusLabel, itemStatusLabel, type OrderStatus, type ItemStatus } from "../../../constants/status";
import { useUpdateOrderStatus } from "../hooks/useUpdateOrderStatus";
import { StockWarningList } from "./StockWarningList";

export function StaffOrderCard({ order }: { order: Order }) {
  const updateStatus = useUpdateOrderStatus();
  const status = (order.status ?? "received") as OrderStatus;
  const items = order.items ?? [];
  // D-32: 모든 항목이 done이어야 서빙완료 가능. 항목이 하나도 없는 예외적인 경우는 막는다.
  const allItemsDone =
    items.length > 0 && items.every((item) => (item.item_status ?? "pending") === "done");

  function change(next: OrderStatus) {
    if (!order.id) return;
    updateStatus.mutate({ orderId: order.id, status: next });
  }

  return (
    <li className={`staff-order-card staff-order-card--${status}`}>
      <div className="staff-order-header">
        <span className="staff-order-table">테이블 {order.table_id}</span>
        <span className="staff-order-status">{orderStatusLabel(status)}</span>
      </div>
      <ul className="staff-order-items">
        {items.map((item) => (
          <li key={item.id} className="staff-order-item-row">
            <span>
              {item.menu_name} x{item.qty}
            </span>
            <span className="staff-order-item-status">
              {itemStatusLabel((item.item_status ?? "pending") as ItemStatus)}
            </span>
          </li>
        ))}
      </ul>
      <span className="staff-order-total">{(order.total_amount ?? 0).toLocaleString()}원</span>
      <StockWarningList order={order} />
      <div className="staff-order-actions">
        {status === "received" && (
          <button
            type="button"
            className="staff-action-btn staff-action-btn--danger"
            disabled={updateStatus.isPending}
            onClick={() => change("cancelled")}
          >
            조리 전 취소
          </button>
        )}
        {status === "cooking" && (
          <button
            type="button"
            className="staff-action-btn"
            disabled={updateStatus.isPending || !allItemsDone}
            onClick={() => change("served")}
          >
            서빙완료로 변경
          </button>
        )}
        {status === "served" && (
          <button
            type="button"
            className="staff-action-btn"
            disabled={updateStatus.isPending}
            onClick={() => change("paid")}
          >
            결제완료로 변경
          </button>
        )}
      </div>
    </li>
  );
}
