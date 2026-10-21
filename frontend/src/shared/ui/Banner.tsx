import type { ReactNode } from "react";
import { Icon, type IconName } from "./Icon";
import "./ui.css";

export type BannerTone = "error" | "warning" | "info";

const TONE_ICON: Record<BannerTone, IconName> = { error: "alert", warning: "alert", info: "info" };

interface BannerProps {
  tone: BannerTone;
  title?: string;
  children?: ReactNode;
  /** 오른쪽 동작 버튼(예: 다시 시도) */
  action?: ReactNode;
}

/** 오류는 role="alert" 배너로 남기고 사라지는 토스트에 쓰지 않는다. */
export function Banner({ tone, title, children, action }: BannerProps) {
  return (
    <div className={`ui-banner ui-banner-${tone}`} role={tone === "error" ? "alert" : "status"}>
      <Icon name={TONE_ICON[tone]} />
      <div className="ui-banner-body">
        {title ? <div className="ui-banner-title">{title}</div> : null}
        {children}
      </div>
      {action}
    </div>
  );
}
