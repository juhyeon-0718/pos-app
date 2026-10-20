# pos-app 디자인 토큰

관리 화면(U-01)부터 이 파일이 토큰의 기준이다. CSS 변수 이름·값은 `owner/prototype/admin.css`의 `:root`와 같다. 값을 바꾸면 이 파일과 `admin.css`를 함께 고친다.
대비율은 WCAG 2.1 상대휘도 공식으로 직접 계산한 값이다(도구 검증 전, 구현 시 DevTools로 재확인). 일반 텍스트 4.5:1, 큰 텍스트·UI 경계·아이콘 3:1 기준.

## 색상 (Colors)

### 중립색 (Neutrals)
- `--color-text-primary`: #212121 (본문, 제목. 흰 배경 16.1:1)
- `--color-text-secondary`: #666666 (설명, 보조 텍스트, placeholder. 흰 배경 5.74:1, `--color-bg-secondary` 위 5.27:1)
- `--color-text-disabled`: #767676 (비활성 컨트롤 글자. `--color-bg-disabled` 위 3.91:1, WCAG 비활성 예외이나 3:1 이상 유지)
- `--color-text-on-fill`: #ffffff (primary·danger·success 채움 배경 위 글자)
- `--color-bg-default`: #ffffff (기본 배경, 카드, 모달)
- `--color-bg-secondary`: #f5f5f5 (페이지 배경, 표 머리글, 행 hover)
- `--color-bg-disabled`: #eeeeee (비활성 컨트롤 배경)
- `--color-border-light`: #e0e0e0 (행 구분선 등 장식용 경계. 기능 경계로 쓰지 않는다)
- `--color-border-default`: #d0d0d0 (카드·표 외곽선. 장식용)
- `--color-border-strong`: #8a8a8a (입력·버튼·체크박스 경계. 흰 배경 3.45:1, 3:1 필요한 UI 경계는 이 값만 쓴다)

### 상태색 (Status)
글자로 쓰는 쌍만 적는다. 상태는 항상 색 + 아이콘 + 텍스트를 함께 쓴다.
- `--color-success`: #2e7d32 (성공·활성. 흰 배경 5.13:1)
- `--color-success-light`: #e8f5e9 (success 글자 4.56:1)
- `--color-error`: #c62828 (오류·삭제. 흰 배경 5.62:1)
- `--color-error-hover`: #b71c1c (danger 버튼 hover. 흰 글자 6.57:1)
- `--color-error-light`: #ffebee (error 글자 4.92:1)
- `--color-warning`: #f57f17 (**채움·테두리·아이콘 전용**. 흰 배경 위 글자 2.65:1로 미달이라 글자에 쓰지 않는다)
- `--color-warning-text`: #7a4100 (경고 글자. 흰 배경 8.13:1, `--color-warning-light` 위 7.41:1)
- `--color-warning-light`: #fff3e0 (경고 배경. `--color-text-primary` 14.7:1)
- `--color-info`: #1565c0 (정보. 흰 배경 5.75:1)
- `--color-info-light`: #e3f2fd (info 글자 5.03:1)

### 인터랙션 (Interactive)
- `--color-primary`: #1565c0 (버튼, 링크, 선택 상태. 흰 글자 5.75:1)
- `--color-primary-hover`: #0d47a1 (흰 글자 8.63:1)
- `--color-primary-active`: #0d35a7 (흰 글자 10.07:1)
- `--color-secondary`: #757575 (흰 글자 4.61:1. 채움 배경으로만 쓰고 `--color-bg-secondary` 위 글자색으로 쓰지 않는다)
- `--color-secondary-hover`: #616161
- `--color-focus-ring`: #1565c0 (포커스 링 2px, offset 2px. 흰 배경 5.75:1)
- `--color-overlay`: rgba(0,0,0,0.5) (모달 뒤 배경)

## 타이포그래피 (Typography)

### 글자 크기 (Font Sizes)
- `--font-size-xs`: 12px (타임스탬프. 관리 화면에서는 쓰지 않음)
- `--font-size-sm`: 13px (라벨, 캡션, 표 머리글, 배지, 도움말)
- `--font-size-base`: 14px (표 본문, 버튼)
- `--font-size-lg`: 16px (입력창 글자, 앱 제목)
- `--font-size-xl`: 18px (모달 제목, 빈 상태 제목)
- `--font-size-2xl`: 20px (섹션 제목)
- `--font-size-3xl`: 24px (페이지 제목)

### 줄높이 (Line Heights)
- `--line-height-tight`: 1.2 (제목)
- `--line-height-normal`: 1.4 (본문)
- `--line-height-relaxed`: 1.6 (모달·빈 상태 안내문)

### 글자 굵기 (Font Weights)
- `--font-weight-regular`: 400
- `--font-weight-medium`: 500 (버튼)
- `--font-weight-semibold`: 600 (라벨, 머리글, 모달 제목)
- `--font-weight-bold`: 700 (페이지 제목, 선택된 탭)

### 숫자 표시
금액·수량 칸은 오른쪽 정렬 + `font-variant-numeric: tabular-nums`. 금액은 `9,000원`, 수량은 `12.5 kg`처럼 천 단위 쉼표와 단위를 붙인다.

## 간격 (Spacing)

### 마진, 패딩 (Margins & Paddings)
- `--spacing-xs`: 4px
- `--spacing-sm`: 8px
- `--spacing-md`: 12px
- `--spacing-lg`: 16px
- `--spacing-xl`: 24px
- `--spacing-2xl`: 32px

### 갭 (Gaps in Flexbox/Grid)
- `--gap-sm`: 8px (인접 요소)
- `--gap-md`: 12px (폼 필드·버튼 사이)
- `--gap-lg`: 16px
- `--gap-xl`: 24px (섹션 사이)

### 크기 (Sizes)
- `--size-touch-min`: 44px (모든 클릭 가능 요소의 최소 높이·너비)
- `--size-control-height`: 44px (입력창·선택창·버튼)
- `--size-row-height`: 56px (표 행 최소 높이)
- `--size-page-max`: 1200px (관리 화면 본문 최대 너비)
- `--size-modal-max`: 520px (모달 최대 너비)

## 모서리 (Border Radius)

- `--radius-sm`: 4px (입력창)
- `--radius-md`: 8px (버튼, 카드, 모달)
- `--radius-lg`: 12px
- `--radius-full`: 9999px (배지, 필터 칩)

## 그림자 (Shadows)

- `--shadow-sm`: 0 1px 2px rgba(0,0,0,0.05) (카드)
- `--shadow-md`: 0 2px 8px rgba(0,0,0,0.1) (토스트)
- `--shadow-lg`: 0 4px 16px rgba(0,0,0,0.15) (모달)

## 경계선 너비 (Border Widths)

- `--border-thin`: 1px
- `--border-default`: 2px (포커스, 오류 입력, 선택된 칩)

## 접근성 (Accessibility)

### 대비율
- 일반 텍스트 4.5:1 이상, 큰 텍스트(18px 이상 또는 14px 굵게)·아이콘·입력/버튼 경계 3:1 이상.
- 색만으로 상태를 구분하지 않는다. 배지는 `아이콘 + 글자`, 오류는 `경고 아이콘 + 문장`, 부족 재고는 `배지 + 행 배경`.
- 비활성 컨트롤은 WCAG 예외 대상이지만 글자 3:1 이상을 유지한다.
- `prefers-reduced-motion`에서는 스피너·스켈레톤 애니메이션을 끈다(`admin.css` 규칙 그대로).

### 최소 터치 영역
모든 인터랙티브 요소는 44×44px 이상. 체크박스는 글자까지 감싼 라벨 전체(높이 44px 이상)를 클릭 영역으로 한다. 표 안 텍스트 버튼도 높이 44px, 가로 44px 이상이다.

### 포커스·키보드
`:focus-visible`에 `--color-focus-ring` 2px 링. 모달은 포커스를 가두고 Esc로 닫으며(저장·삭제 처리 중 제외) 닫힌 뒤 열었던 버튼으로 돌아간다.

## 반응형 (Responsive)

- **모바일(손님 QR 주문)**: 320px 이상, 한 손 조작
- **태블릿(직원)**: 768px 이상, 빠른 처리용 레이아웃
- **데스크톱(사장)**: 1024px 이상, 관리·분석. 사장 관리 화면은 1024px 기준으로 설계하고 그 아래는 표 가로 스크롤을 허용한다.
- **주방 화면**: 2m 거리에서 가독 가능(44pt 이상 텍스트)

## 폰트 스택 (Font Stack)

```css
--font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", "Malgun Gothic", sans-serif;
```

- 시스템 폰트 우선. 웹폰트 파일을 새로 내려받거나 포함하지 않는다(외부 에셋 없음).
- Noto Sans KR은 사용자 기기에 설치돼 있을 때만 쓰이는 대체 이름이다. 라이선스: SIL OFL 1.1. 출처는 `assets-license.md`.

## 변경 이력

- U-01: `--color-text-disabled` #cccccc → #767676(1.61:1 → 3.91:1). `--color-border-strong`, `--color-bg-disabled`, `--color-error-hover`, `--color-warning-text`, `--color-text-on-fill`, `--color-focus-ring`, `--color-overlay`, `--size-*` 추가. `--font-family`에 Malgun Gothic 추가.
- U-01: 이전 표기의 대비율 오류 정정. `--color-warning`은 글자색으로 4.5:1을 만족하지 못한다(2.65:1). `--color-border-default`는 3:1 미달이라 UI 경계로 쓰지 않는다(1.54:1).
- 기존 로그인·손님·주방·직원 화면이 이 토큰을 쓰는지는 U-02에서 점검한다. 이번 변경으로 그 화면은 수정하지 않았다.

## 브랜드 로고 (Brand)

파일은 `docs/design/brand/`에 있다. 사용 예와 대비 확인은 `brand/logo-preview.html`. 정주현이 저장소 반영을 승인했다(공개 저장소 D-28, 매장 로고는 상표성 자산이라 코드·문구에서 다른 용도로 쓰지 않는다).

- `logo-original.jpg`: 원본(7087×2362, 흰 배경 검정). 인쇄·QR 카드 원본용이며 화면에는 쓰지 않는다.
- `logo-black.png` / `logo-white.png`: 투명 배경 960px. 원본 구성 그대로. `-sm`은 480px.
- `logo-compact-black.png` / `logo-compact-white.png`: 투명 배경 640px. 75MHz 아래에 LIVE PUB을 크게 다시 배치한 축약형. 작은 영역용.

### 사용 규칙
- **LIVE PUB은 항상 보인다.** 로고에서 LIVE PUB을 빼거나 "75MHz"만 쓰지 않는다.
- **최소 크기**: 원본 구성은 높이 120px 이상(LIVE PUB 글자 약 10px). 그보다 작은 영역(상단 바 등)은 축약형을 높이 56px 이상으로 쓴다. 축약형 56px에서 LIVE PUB 글자는 약 7px이다.
- **색**: 밝은 배경(`--color-bg-default` 21:1, `--color-bg-secondary` 19.26:1)은 검정, 어두운 배경(#212121 16.1:1, #121212 18.73:1)과 `--color-primary` 위(5.75:1)는 흰색. 검정 로고는 `--color-primary` 위에서 3.65:1이라 쓰지 않는다.
- **여백**: 로고 높이의 25% 이상을 사방에 비운다. 늘리거나 회전하거나 색을 바꾸지 않는다.
- **접근성**: `alt="75MHz LIVE PUB"`. 장식으로만 쓰는 반복 배치는 `alt=""`.
- **화면별**: 사장 상단 바는 축약형 56px(구분선 + 화면 이름 옆에 배치). 손님 화면 첫 화면은 축약형 80px 이상. 주방·직원 화면은 어두운 배경이면 흰색 축약형. 확정은 각 화면 명세에서 한다.
- 축약형은 원본 로고를 재배치한 파생 파일이다. 정주현이 모양을 확인하기 전까지는 시안 상태다.
