// U-03 공용 아이콘 path. 직접 그린 SVG(docs/design/components/prototype/ui.js와 같은 값).
// 외부 아이콘 라이브러리는 쓰지 않는다(도입은 정주현 확인 대상).

export const ICON_PATHS = {
  check: "M5 12l5 5 9-10",
  x: "M6 6l12 12M18 6L6 18",
  plus: "M12 5v14M5 12h14",
  minus: "M5 12h14",
  clock: "M12 7v5l3 2",
  flame: "M12 3c1 4 5 5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-1-5 1-9z",
  bell: "M6 16V11a6 6 0 0 1 12 0v5l2 2H4zM10 20h4",
  alert: "M12 4l9 16H3zM12 10v4M12 17v.5",
  ban: "M6 6l12 12",
  cart: "M3 4h2l2 11h11l2-8H7",
  receipt: "M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6",
  user: "M4 21a8 8 0 0 1 16 0",
  lock: "M8 11V8a4 4 0 0 1 8 0v3",
  refresh: "M20 12a8 8 0 1 1-2.5-5.8M20 4v5h-5",
  info: "M12 11v6M12 7.5v.5",
  utensils: "M6 3v8a2 2 0 0 0 2 2v8M10 3v8M6 7h4M17 3c-2 2-3 5-3 8h3v10",
  inbox: "M3 13l3-8h12l3 8v6H3zM3 13h5l1 3h6l1-3h5",
  spinner: "M12 3a9 9 0 1 0 9 9",
  hash: "M5 9h14M5 15h14M10 4L8 20M16 4l-2 16",
  dish: "M3 15h18a9 9 0 0 0-18 0zM2 19h20M12 6V4",
} as const;

export type IconName = keyof typeof ICON_PATHS;
