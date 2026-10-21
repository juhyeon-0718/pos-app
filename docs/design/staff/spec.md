# U-05 직원 화면 명세 (시안 단계, U-03)

상태: 메인 화면 시안만. 기본·로딩·빈 상태·오류·비활성 상태는 U-05 상세 명세에서 정의한다.
프로토타입: `prototype/staff.html` (1024×768 태블릿 가로 기준).

## 구성
- 상단 바: 로고, 화면 이름, 실시간 연결 상태, "대리 주문"(primary, 56px).
- 필터 칩: 전체 / 접수 / 조리 중 / 서빙 완료. 칩마다 건수(숫자 배지). 결제 완료·취소는 기본으로 숨김.
- 주문 카드(2열): 테이블 번호, 상태 배지(큰), 항목·수량, 접수 시각·경과, 합계, 액션 버튼(56px).
- 액션은 상태별 한 개: 접수 → "주문 취소"(text danger, 확인 모달), 조리 중 → "서빙 완료"(success, 모든 항목 `item_status=done`일 때만 활성. 비활성이면 이유를 글자로 안내), 서빙 완료 → "결제 완료"(primary).
- 지금 눌러야 할 카드(서빙 가능, 결제 대기)는 `--color-primary` 2px 테두리로 구분한다.

## 사용 토큰
`--size-touch-lg`, `--font-size-3xl/xl/lg`, `--color-primary`, 공용 Badge(주문 상태 5종), Button, Card(U-03 components).

## 데이터 (openapi.yaml 기준)
Order: `id`, `table_id`, `status`, `total_amount`, `created_at`, `items[]`(`menu_name`, `qty`, `item_status`), `stock_warnings[]`. 상태 변경은 `PATCH /orders/{order_id}/status`(received→cooking→served→paid, cancelled).

## 계약 요청 (민준 님께)
1. Order에 `table_no`가 필요하다(주방 요청 1번과 같음).
2. 직원 대리 주문 화면의 테이블 선택은 `GET /tables`로 가능하다. 대리 주문 화면은 U-05 상세 명세에서 다룬다.
3. `stock_warnings[]` 표시 위치(카드 배너)는 상세 명세에서 정한다.

## 대비
상태 배지 대비는 `../components/spec.md`. 칩 선택 상태는 `--color-primary` on `--color-info-light` 5.03:1. 직접 계산한 값이며 도구 검증 전.

## 완료 조건 (구현자, 잠정)
1. 모든 버튼 높이 56px 이상, 칩 56px 이상.
2. 취소는 확인 모달을 거친다. 결제·서빙은 한 번 눌러 처리하고 실패하면 카드 안에 오류 배너.
3. 토큰 변수만 사용.
