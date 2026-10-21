# U-03 공용 컴포넌트 명세 (시안 단계)

상태: 시안(메인 화면만). 상태별 상세·키보드·ARIA 표는 U-04 이후 화면 명세와 함께 확정한다.
프로토타입: `prototype/components.html` (정적 HTML, `ui.js`는 자체 SVG 아이콘, 외부 에셋 없음). 토큰은 `../DESIGN.md` 값만 쓴다.

## 범위
Button, Badge(주문 상태), Card, Banner, Modal, 상태 표시(로딩·빈 상태·오류). F-09(`shared/ui/`) 추출 범위와 같다. 다른 컴포넌트는 화면 작업 중 3곳 이상 반복될 때만 추가한다.

## 컴포넌트와 토큰
- **Button** `primary / secondary / danger / success / text`. 높이 `--size-control-height` 44px, 큰 버튼 `--size-touch-lg` 56px(손님·직원), 주방 `--size-touch-kitchen` 88px. 비활성은 `--color-bg-disabled` + `--color-text-disabled`, 처리 중은 스피너 + 글자 + `aria-busy`.
- **Badge** 주문 상태 5종(openapi `OrderStatus`). 색 + 아이콘 + 글자를 항상 함께 쓴다.
  - received 접수(inbox, `--color-info-light`/`--color-info`)
  - cooking 조리 중(flame, `--color-warning-light`/`--color-warning-text`, 테두리 `--color-warning`)
  - served 서빙 완료(check, `--color-success-light`/`--color-success`)
  - paid 결제 완료(receipt, `--color-bg-secondary`/`--color-text-secondary`)
  - cancelled 취소(x, `--color-error-light`/`--color-error`)
  - 기본 13px, 손님·직원 큰 배지 16px(`badge-lg`).
- **Card** `--color-bg-default`, `--border-thin` `--color-border-light`, `--radius-md`, `--shadow-sm`. 주의가 필요한 카드(직원: 처리할 차례)는 `--border-default` `--color-primary` 테두리.
- **Banner** error / warning / info. 오류는 `role="alert"` 배너로 남기고 자동으로 사라지는 토스트에 쓰지 않는다.
- **Modal** 데스크톱은 가운데(`--size-modal-max`), 모바일은 아래 시트(`--size-phone-max`). 포커스 가두기, Esc 닫기, 닫은 뒤 열었던 버튼으로 복귀.
- **상태 표시** 로딩(스켈레톤 + "불러오는 중"), 빈 상태(아이콘 + 제목 + 한 줄 안내), 오류(경고 아이콘 + 문장 + "다시 시도").

## 이번 시안에서 추가한 토큰 (DESIGN.md와 admin.css에 함께 반영)
`--color-success-hover` #1b5e20(흰 글자 7.87:1), `--size-touch-lg` 56px, `--size-touch-kitchen` 88px, `--size-phone-max` 480px, `--font-size-kitchen-meta` 32px, `--font-size-kitchen-body` 59px(44pt), `--font-size-kitchen-title` 72px.

## 대비 (WCAG 2.1 공식으로 직접 계산, 도구 검증 전)
- 흰 글자 on `--color-success-hover` 7.87:1, `--color-success` 5.13:1, `--color-primary` 5.75:1.
- `--color-info` on `--color-info-light` 5.03:1, `--color-warning-text` on `--color-warning-light` 7.41:1, `--color-error` on `--color-error-light` 4.92:1, `--color-success` on `--color-success-light` 4.56:1.

## 완료 조건 (구현자)
1. `frontend/src/shared/ui/`에 Button, Badge, Card, Banner, Modal, 상태 표시를 만들고 컴포넌트별 테스트를 둔다.
2. 색·크기·간격은 토큰 변수만 쓴다. 하드코딩 값이 없어야 한다.
3. feature 폴더끼리 import하지 않고 공용은 `shared/ui`만 쓴다(D-25).
4. Badge는 아이콘 + 글자 없이 색만으로 렌더하지 않는다.
5. 클릭 요소 높이·너비 44px 이상.

## 열린 항목
- 아이콘은 직접 그린 SVG(라이선스 문제 없음). 구현에서 같은 path를 쓴다. 아이콘 라이브러리 도입은 정주현 확인이 필요하다.
