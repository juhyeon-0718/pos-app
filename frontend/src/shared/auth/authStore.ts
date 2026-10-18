// 직원/주방/사장 공용 로그인 상태 (Zustand). features/ 간 직접 참조를 피하려고
// features/ 밖 shared/에 둔다 — kitchen·staff·owner 화면이 각자 여기서 가져다 쓴다.
// 새로고침해도 로그인이 유지되도록 sessionStorage에 동기화한다(태블릿 재시작 전까지).

import { create } from "zustand";
import type { Role } from "../../api/auth";

const STORAGE_KEY = "pos:auth";

interface StoredAuth {
  accessToken: string;
  role: Role;
}

interface AuthState {
  accessToken: string | null;
  role: Role | null;
  setAuth: (accessToken: string, role: Role) => void;
  logout: () => void;
}

function loadStored(): StoredAuth | null {
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredAuth;
  } catch {
    return null;
  }
}

const stored = loadStored();

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: stored?.accessToken ?? null,
  role: stored?.role ?? null,
  setAuth: (accessToken, role) => {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ accessToken, role }));
    set({ accessToken, role });
  },
  logout: () => {
    sessionStorage.removeItem(STORAGE_KEY);
    set({ accessToken: null, role: null });
  },
}));
