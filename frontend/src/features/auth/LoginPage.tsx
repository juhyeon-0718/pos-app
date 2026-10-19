// 직원/주방/사장 공용 로그인 화면. 역할별 분기는 상위(App.tsx)에서 role 값으로 처리한다.

import { useState, type FormEvent } from "react";
import { useLogin } from "./useLogin";
import "./auth.css";

export function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const loginMutation = useLogin();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    loginMutation.mutate({ username, password });
  }

  return (
    <main className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>로그인</h1>
        <label>
          아이디
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label>
          비밀번호
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        <button type="submit" disabled={loginMutation.isPending}>
          {loginMutation.isPending ? "로그인 중..." : "로그인"}
        </button>
        {loginMutation.isError && (
          <p className="login-error" role="alert">
            아이디 또는 비밀번호가 올바르지 않습니다.
          </p>
        )}
      </form>
    </main>
  );
}
