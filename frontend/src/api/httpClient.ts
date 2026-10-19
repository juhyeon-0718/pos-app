// 인증이 필요한(bearerAuth) API 호출 공용 래퍼. 401을 받으면 즉시 로그아웃시켜
// 만료된 토큰으로 빈 데이터만 계속 폴링하는 상태를 막는다 (kitchen/staff/owner 공통).

import { useAuthStore } from "../hooks/useAuthStore";

export async function authorizedFetch(url: string, init?: RequestInit): Promise<Response> {
  const res = await fetch(url, init);
  if (res.status === 401) {
    useAuthStore.getState().logout();
  }
  return res;
}
