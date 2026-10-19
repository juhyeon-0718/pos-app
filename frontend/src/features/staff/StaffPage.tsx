import { useAllOrders } from "./hooks/useAllOrders";
import { StaffOrderCard } from "./components/StaffOrderCard";
import { StaffNewOrderForm } from "./components/StaffNewOrderForm";
import { LoginPage } from "../auth/LoginPage";
import { useAuthStore } from "../../hooks/useAuthStore";
import "./staff.css";

export function StaffPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const role = useAuthStore((s) => s.role);
  const orders = useAllOrders();

  if (!accessToken) {
    return <LoginPage />;
  }

  if (role !== "staff") {
    return (
      <main className="staff-page">
        <p className="staff-role-error">직원 계정으로 로그인해 주세요.</p>
      </main>
    );
  }

  return (
    <main className="staff-page">
      <h1>직원 화면</h1>
      <StaffNewOrderForm />

      <section>
        <h2>주문 목록</h2>
        {orders.isLoading && <p>불러오는 중...</p>}
        {orders.isError && <p className="staff-error">주문 목록을 불러오지 못했습니다.</p>}
        {orders.data && orders.data.length === 0 && <p>진행 중인 주문이 없습니다.</p>}
        {orders.data && orders.data.length > 0 && (
          <ul className="staff-order-list">
            {orders.data.map((order) => (
              <StaffOrderCard key={order.id} order={order} />
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
