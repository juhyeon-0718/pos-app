import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// 자동 cleanup이 vitest 환경을 못 잡는 경우가 있어 명시적으로 등록한다.
// 이게 없으면 이전 테스트의 렌더가 DOM에 남아 다음 테스트의 쿼리가 잘못 매칭된다.
afterEach(() => {
  cleanup();
});
