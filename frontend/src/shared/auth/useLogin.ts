import { useMutation } from "@tanstack/react-query";
import { login, type LoginResponse } from "../../api/auth";
import { useAuthStore } from "./authStore";

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth);

  return useMutation<LoginResponse, Error, { username: string; password: string }>({
    mutationFn: ({ username, password }) => login(username, password),
    onSuccess: (res) => setAuth(res.access_token, res.role),
  });
}
