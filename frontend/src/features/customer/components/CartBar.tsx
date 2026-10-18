// 화면 하단 고정 장바구니 바 (한손 조작 기준). 수량 조절 + 주문 버튼.
// 주문 버튼은 전송 중 비활성화해 중복 클릭 시 추가 네트워크 요청을 막되,
// 혹시 두 번 호출되어도 api/orders.ts가 같은 draftId -> 같은 Idempotency-Key를 재사용한다 (D-15).

import { useCartStore } from "../store/cartStore";
import { useCreateOrder } from "../hooks/useCreateOrder";

export function CartBar({ tableSessionToken }: { tableSessionToken: string | null }) {
  const items = useCartStore((s) => s.items);
  const setQty = useCartStore((s) => s.setQty);
  const totalAmount = useCartStore((s) => s.totalAmount());
  const createOrder = useCreateOrder(tableSessionToken);

  if (items.length === 0) return null;

  return (
    <div className="cart-bar">
      <ul className="cart-items">
        {items.map((item) => (
          <li key={item.menuId} className="cart-item-row">
            <span className="cart-item-name">{item.name}</span>
            <div className="cart-item-qty">
              <button
                type="button"
                aria-label={`${item.name} 수량 줄이기`}
                onClick={() => setQty(item.menuId, item.qty - 1)}
              >
                −
              </button>
              <span>{item.qty}</span>
              <button
                type="button"
                aria-label={`${item.name} 수량 늘리기`}
                onClick={() => setQty(item.menuId, item.qty + 1)}
              >
                +
              </button>
            </div>
          </li>
        ))}
      </ul>
      <div className="cart-summary">
        <span className="cart-total">총 {totalAmount.toLocaleString()}원</span>
        <button
          type="button"
          className="order-submit-btn"
          disabled={createOrder.isPending || !tableSessionToken}
          onClick={() => createOrder.mutate()}
        >
          {createOrder.isPending ? "주문 중..." : "주문하기"}
        </button>
      </div>
      {createOrder.isError && (
        <p className="cart-error" role="alert">
          주문 실패. 다시 시도해 주세요.
        </p>
      )}
    </div>
  );
}
