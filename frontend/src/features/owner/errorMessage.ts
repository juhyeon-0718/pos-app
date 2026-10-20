import { ApiError } from "../../api/ownerFetch";

// 409·422·403은 서버 detail을 그대로(텍스트로만) 보여 주고, 없으면 기본 문구를 쓴다.
export function errorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 409) return err.detail ?? "다른 데이터에서 사용 중이라 처리할 수 없습니다.";
    if (err.status === 422) return err.detail ?? "입력값을 확인해 주세요.";
    if (err.status === 403) return "사장 권한이 필요합니다.";
  }
  return "처리하지 못했습니다. 잠시 후 다시 시도해 주세요.";
}
