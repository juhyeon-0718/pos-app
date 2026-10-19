// 직원 화면은 stock_warnings를 노출한다(손님 화면과 반대, D-23 지시).

import type { Order } from "../../../api/orders";

export function StockWarningList({ order }: { order: Order }) {
  const warnings = order.stock_warnings ?? [];
  if (warnings.length === 0) return null;

  return (
    <ul className="stock-warning-list" role="alert">
      {warnings.map((w) => (
        <li key={w.ingredient_id} className="stock-warning-item">
          재고 부족: {w.name} (현재 {w.current_stock} / 필요 {w.required})
        </li>
      ))}
    </ul>
  );
}
