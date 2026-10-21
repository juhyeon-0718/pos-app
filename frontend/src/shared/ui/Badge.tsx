import { orderStatusLabel, type OrderStatus } from "../../constants/status";
import { Icon, type IconName } from "./Icon";
import "./ui.css";

// 주문 상태 5종: 색 + 아이콘 + 글자를 항상 함께 그린다(색만으로 구분하지 않음).
const STATUS_ICON: Record<OrderStatus, IconName> = {
  received: "inbox",
  cooking: "flame",
  served: "check",
  paid: "receipt",
  cancelled: "x",
};

interface BadgeProps {
  status: OrderStatus;
  /** 손님·직원 화면의 큰 배지(16px) */
  large?: boolean;
}

export function Badge({ status, large = false }: BadgeProps) {
  return (
    <span className={`ui-badge ui-badge-${status}${large ? " ui-badge-lg" : ""}`}>
      <Icon name={STATUS_ICON[status]} />
      {orderStatusLabel(status)}
    </span>
  );
}
