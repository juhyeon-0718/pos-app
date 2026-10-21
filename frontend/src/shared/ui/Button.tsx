import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Icon, type IconName } from "./Icon";
import "./ui.css";

export type ButtonVariant = "primary" | "secondary" | "danger" | "success" | "text" | "text-danger";
// md 44px(--size-control-height), lg 56px(손님·직원), kitchen 88px(주방)
export type ButtonSize = "md" | "lg" | "kitchen";

interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "className"> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  /** 처리 중: 스피너 + 글자, aria-busy, 클릭 불가 */
  loading?: boolean;
  block?: boolean;
  icon?: IconName;
  children: ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  block = false,
  icon,
  type = "button",
  disabled,
  children,
  ...rest
}: ButtonProps) {
  const classes = ["ui-btn", `ui-btn-${variant}`, size !== "md" ? `ui-btn-${size}` : "", block ? "ui-btn-block" : ""]
    .filter(Boolean)
    .join(" ");
  return (
    <button type={type} className={classes} disabled={disabled || loading} aria-busy={loading || undefined} {...rest}>
      {loading ? <Icon name="spinner" /> : icon ? <Icon name={icon} /> : null}
      {children}
    </button>
  );
}
