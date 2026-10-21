// U-03 공용 아이콘. path 데이터는 iconPaths.ts(직접 그린 SVG, 외부 라이브러리 없음).

import { ICON_PATHS, type IconName } from "./iconPaths";
import "./ui.css";

export type { IconName } from "./iconPaths";

// path만으로 그릴 수 없는 도형(원, 사각형)
function Extra({ name }: { name: IconName }) {
  switch (name) {
    case "clock":
    case "ban":
    case "info":
      return <circle cx="12" cy="12" r="9" />;
    case "cart":
      return (
        <>
          <circle cx="9" cy="20" r="1.4" />
          <circle cx="17" cy="20" r="1.4" />
        </>
      );
    case "user":
      return <circle cx="12" cy="8" r="4" />;
    case "lock":
      return <rect x="5" y="11" width="14" height="10" rx="2" />;
    default:
      return null;
  }
}

interface IconProps {
  name: IconName;
  /** 추가 클래스 */
  className?: string;
}

/** 장식용 아이콘: 항상 aria-hidden. 의미는 옆의 글자가 전달한다. */
export function Icon({ name, className }: IconProps) {
  const spin = name === "spinner" ? " ui-spin" : "";
  return (
    <svg
      className={`ui-icon${spin}${className ? ` ${className}` : ""}`}
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
      data-icon={name}
    >
      <Extra name={name} />
      <path d={ICON_PATHS[name]} />
    </svg>
  );
}
