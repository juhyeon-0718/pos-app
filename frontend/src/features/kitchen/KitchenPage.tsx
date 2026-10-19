import { useKitchenQueue } from "./hooks/useKitchenQueue";
import { KitchenItemCard } from "./components/KitchenItemCard";
import { LoginPage } from "../auth/LoginPage";
import { useAuthStore } from "../../hooks/useAuthStore";
import "./kitchen.css";

export function KitchenPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const role = useAuthStore((s) => s.role);
  const queue = useKitchenQueue();

  if (!accessToken) {
    return <LoginPage />;
  }

  if (role !== "kitchen") {
    return (
      <main className="kitchen-page">
        <p className="kitchen-role-error">주방 계정으로 로그인해 주세요.</p>
      </main>
    );
  }

  return (
    <main className="kitchen-page">
      <h1>주방 큐</h1>
      {queue.isLoading && <p>불러오는 중...</p>}
      {queue.isError && <p className="kitchen-error">큐를 불러오지 못했습니다.</p>}
      {queue.data && queue.data.length === 0 && <p>대기 중인 항목이 없습니다.</p>}
      {queue.data && queue.data.length > 0 && (
        <ul className="kitchen-queue">
          {queue.data.map((item) => (
            <KitchenItemCard key={item.id} item={item} />
          ))}
        </ul>
      )}
    </main>
  );
}
