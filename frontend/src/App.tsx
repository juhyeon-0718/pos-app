import { CustomerOrderPage } from "./features/customer/CustomerOrderPage";
import { KitchenPage } from "./features/kitchen/KitchenPage";
import { OwnerPage } from "./features/owner/OwnerPage";
import { StaffPage } from "./features/staff/StaffPage";

// 라우터 없이 경로로만 분기한다(F-06에서 owner 추가 시 같은 패턴 확장).
function App() {
  const path = window.location.pathname;

  if (path.startsWith("/kitchen")) {
    return <KitchenPage />;
  }

  if (path.startsWith("/staff")) {
    return <StaffPage />;
  }

  if (path.startsWith("/owner")) {
    return <OwnerPage />;
  }

  return <CustomerOrderPage />;
}

export default App;
