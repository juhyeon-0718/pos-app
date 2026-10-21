import type { HTMLAttributes } from "react";
import "./ui.css";

interface CardProps extends Omit<HTMLAttributes<HTMLElement>, "className"> {
  /** 지금 처리할 차례인 카드(직원 화면): --color-primary 2px 테두리 */
  attention?: boolean;
  /** 목록 안에서 쓰면 "li" */
  as?: "div" | "li" | "section" | "article";
}

export function Card({ attention = false, as: Tag = "div", children, ...rest }: CardProps) {
  return (
    <Tag className={`ui-card${attention ? " ui-card-attention" : ""}`} {...rest}>
      {children}
    </Tag>
  );
}
