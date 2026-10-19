// 주문 단위 카드. 상태별로 가능한 다음 동작만 버튼으로 노출한다.
// - received: 조리 전 취소(직원 가능). 조리 시작 후 취소는 사장 전용이라 F-05에는 없다(D-19).
// - cooking: 서빙완료로 변경
// - served: 결제완료로 변경
// - paid/cancelled: 동작 없음

import type { Order } from "../../../api/orders";
import { orderStatusLabel, type OrderStatus } from "../../../constants/status";
import { useUpdateOrderStatus } from "../hooks/useUpdateOrderStatus";
import { StockWarningList } from "./StockWarningList";

export function StaffOrderCard({ order }: { order: Order }) {
  const updateStatus = useUpdateOrderStatus();
  const status = (order.status ?? "received") as OrderStatus;

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
        {order.items?.map((item) => (
          <li key={item.id}>
            {item.menu_name} x{item.qty}
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
            disabled={updateStatus.isPending}
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
