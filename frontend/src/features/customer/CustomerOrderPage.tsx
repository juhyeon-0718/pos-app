// 손님 QR 주문 화면 전체 플로우:
// POST /tables/{table_id}/session -> GET /menus -> 장바구니 -> POST /orders -> GET /orders/mine 폴링

import { useTableSession } from "./hooks/useTableSession";
import { useMenus } from "./hooks/useMenus";
import { useOrdersMine } from "./hooks/useOrdersMine";
import { MenuList } from "./components/MenuList";
import { CartBar } from "./components/CartBar";
import { OrderStatusPanel } from "./components/OrderStatusPanel";
import "./customer.css";

export function CustomerOrderPage() {
  const session = useTableSession();
  const menus = useMenus(session.token);
  const orders = useOrdersMine(session.token ?? "");

  if (session.error === "INVALID_QR_LINK") {
    return (
      <main className="customer-page">
        <p className="session-error">
          올바르지 않은 QR입니다. 테이블의 QR코드를 다시 스캔해 주세요.
        </p>
      </main>
    );
  }

  if (session.error === "SESSION_CREATE_FAILED") {
    return (
      <main className="customer-page">
        <p className="session-error">세션 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.</p>
      </main>
    );
  }

  if (session.loading || !session.token) {
    return (
      <main className="customer-page">
        <p className="session-loading">테이블 연결 중...</p>
      </main>
    );
  }

  return (
    <main className="customer-page">
      <section className="order-status-section">
        <h2>내 주문</h2>
        <OrderStatusPanel orders={orders.data} />
      </section>

      <section className="menu-section">
        <h2>메뉴</h2>
        {menus.isLoading && <p>메뉴를 불러오는 중...</p>}
        {menus.isError && <p className="menu-error">메뉴를 불러오지 못했습니다.</p>}
        {menus.data && <MenuList menus={menus.data} />}
      </section>

      <CartBar tableSessionToken={session.token} />
    </main>
  );
}
