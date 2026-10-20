import type { ErrorText } from "../errorMessage";

// 오류는 토스트가 아니라 배너로 남긴다(명세 §1). 서버 문구도 평문(textContent)으로만 렌더링한다(D-24).
export function ErrorBanner({ text }: { text: ErrorText }) {
  return (
    <div role="alert" className="owner-banner">
      <strong>⚠ {text.title}</strong>
      {text.sub && <span>{text.sub}</span>}
    </div>
  );
}
