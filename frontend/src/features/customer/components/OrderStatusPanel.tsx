// 손님 본인 주문 상태 목록. stock_warnings는 손님 화면에 절대 노출하지 않는다 (D-23 지시).
// 상태 라벨은 constants/status.ts 매핑만 사용 — API는 영문 enum만 내려준다 (D-18).

import type { Order } from "../../../api/orders";
import { orderStatusLabel, type OrderStatus } from "../../../constants/status";

export function OrderStatusPanel({ orders }: { orders: Order[] | undefined }) {
  if (!orders || orders.length === 0) {
    return <p className="orders-empty">아직 주문이 없습니다.</p>;
  }

  return (
    <ul className="order-status-list">
      {orders.map((order) => (
        <li key={order.id} className="order-status-row">
          <div className="order-status-header">
            <span className="order-status-badge">
              {orderStatusLabel(order.status as OrderStatus)}
            </span>
            <span className="order-total">{(order.total_amount ?? 0).toLocaleString()}원</span>
          </div>
          <ul className="order-items">
            {order.items?.map((item) => (
              <li key={item.id}>
                {item.menu_name} x{item.qty}
              </li>
            ))}
          </ul>
          {/* stock_warnings는 의도적으로 렌더링하지 않는다 — 손님 화면 노출 금지 */}
        </li>
      ))}
    </ul>
  );
}
