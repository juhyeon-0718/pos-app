import { CustomerOrderPage } from "./features/customer/CustomerOrderPage";
import { KitchenPage } from "./features/kitchen/KitchenPage";

// 라우터 없이 경로로만 분기한다(F-05/F-06에서 staff/owner 추가 시 같은 패턴 확장).
function App() {
  const path = window.location.pathname;

  if (path.startsWith("/kitchen")) {
    return <KitchenPage />;
  }

  return <CustomerOrderPage />;
}

export default App;
