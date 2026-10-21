/// <reference types="node" />
// tokens.css(앱)와 admin.css(디자인 프로토타입 :root)의 토큰이 어긋나지 않는지 비교한다.
// 기준은 docs/design/DESIGN.md. 값을 바꾸면 DESIGN.md, admin.css, tokens.css를 함께 고친다.
// (vitest는 .css?raw를 빈 문자열로 돌려주므로 파일을 직접 읽는다.)

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

// vitest는 frontend/ 에서 실행한다(npm test). jsdom에서는 import.meta.url이 file URL이 아니라 cwd 기준으로 읽는다.
const tokensCss = readFileSync(resolve(process.cwd(), "src/styles/tokens.css"), "utf-8");
const adminCss = readFileSync(resolve(process.cwd(), "../docs/design/owner/prototype/admin.css"), "utf-8");

function rootTokens(css: string): Map<string, string> {
  const root = /:root\s*\{([^}]*)\}/.exec(css);
  if (!root) throw new Error(":root 블록을 찾지 못했습니다");
  const map = new Map<string, string>();
  for (const m of root[1].matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)) {
    map.set(m[1], m[2].replace(/\s+/g, " ").trim());
  }
  return map;
}

describe("디자인 토큰 동기화", () => {
  const app = rootTokens(tokensCss);
  const design = rootTokens(adminCss);

  it("두 파일 모두 토큰을 읽었다", () => {
    expect(app.size).toBeGreaterThan(60);
    expect(design.size).toBeGreaterThan(60);
  });

  it("admin.css의 모든 토큰이 tokens.css에 같은 값으로 있다", () => {
    const diff = [...design]
      .filter(([k, v]) => app.get(k) !== v)
      .map(([k, v]) => `${k}: 디자인=${v} 앱=${app.get(k)}`);
    expect(diff).toEqual([]);
  });

  it("tokens.css에 admin.css에 없는 토큰이 없다", () => {
    const extra = [...app.keys()].filter((k) => !design.has(k));
    expect(extra).toEqual([]);
  });
});
