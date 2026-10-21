// 주방 원거리 가독성 기준(D-23): 큰 글씨, 고대비 색상 — 조리대에서 몇 걸음 떨어져도
// 상태 식별 가능해야 한다. 다음 상태로 넘기는 버튼 하나만 둔다(pending -> cooking -> done).

import type { OrderItem } from "../../../api/kitchen";
import type { ItemStatus } from "../../../constants/status";
import { itemStatusLabel, itemActionLabel } from "../../../constants/status";
import { tableLabel } from "../../../constants/table";
import { useUpdateItemStatus } from "../hooks/useUpdateItemStatus";

const NEXT_STATUS: Record<ItemStatus, ItemStatus | null> = {
  pending: "cooking",
  cooking: "done",
  done: null,
};

export function KitchenItemCard({ item }: { item: OrderItem }) {
  const updateStatus = useUpdateItemStatus();
  const status = (item.item_status ?? "pending") as ItemStatus;
  const next = NEXT_STATUS[status];

  return (
    <li className={`kitchen-item kitchen-item--${status}`}>
      <span className="kitchen-item-table">{tableLabel(item.table_no)}</span>
      <div className="kitchen-item-main">
        <span className="kitchen-item-name">{item.menu_name}</span>
        <span className="kitchen-item-qty">x{item.qty}</span>
      </div>
      <span className="kitchen-item-status">{itemStatusLabel(status)}</span>
      {next && (
        <button
          type="button"
          className="kitchen-item-btn"
          disabled={updateStatus.isPending}
          onClick={() =>
            item.id && updateStatus.mutate({ itemId: item.id, status: next })
          }
        >
          {itemActionLabel(status)}
        </button>
      )}
    </li>
  );
}
