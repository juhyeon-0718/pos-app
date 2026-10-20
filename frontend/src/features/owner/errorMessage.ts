import { ApiError } from "../../api/ownerFetch";

export interface ErrorText {
  title: string;
  sub: string;
}

export type ErrorKind = "menu-save" | "ingredient-save" | "menu-action" | "ingredient-pause";

const SERVER = "서버에 문제가 생겼어요. 잠시 후 다시 시도해 주세요.";
const DETAIL_MAX = 200;

// U-01 명세 §1·§2.3·§3.3·§3.4 문구. 서버 detail이 있으면 보조 문장 자리에 평문으로 쓴다(200자 제한).
export function errorText(err: unknown, kind: ErrorKind, name?: string): ErrorText {
  const detail = err instanceof ApiError && err.detail ? err.detail.slice(0, DETAIL_MAX) : null;
  if (err instanceof ApiError) {
    if (err.status === 403) return { title: "사장 계정만 관리할 수 있어요.", sub: "" };
    if (err.status === 409) {
      if (kind === "menu-save") return { title: "같은 이름의 메뉴가 이미 있어요.", sub: detail ?? "다른 이름으로 바꿔서 저장해 주세요." };
      if (kind === "ingredient-save") return { title: "같은 이름의 식재료가 이미 있어요.", sub: detail ?? "다른 이름으로 바꿔서 저장해 주세요." };
      if (kind === "ingredient-pause") {
        return {
          title: `"${name ?? "식재료"}"은(는) 다른 곳에서 사용 중이라 사용중지로 바꿀 수 없어요.`,
          sub: detail ?? "사용하는 곳에서 먼저 이 식재료를 빼 주세요.",
        };
      }
    }
    if (err.status === 422) {
      if (kind === "menu-save") return { title: "입력한 내용을 저장하지 못했어요.", sub: detail ?? "이름과 가격을 다시 확인해 주세요." };
      if (kind === "ingredient-save") return { title: "입력한 내용을 저장하지 못했어요.", sub: detail ?? "이름, 단위와 숫자 항목을 다시 확인해 주세요." };
    }
  }
  if (kind === "menu-action" || kind === "ingredient-pause") {
    return { title: "처리하지 못했어요.", sub: "잠시 후 다시 시도해 주세요." };
  }
  return { title: SERVER, sub: "" };
}
