# U-04 주방 화면 명세 (시안 단계, U-03)

상태: 메인 화면 시안만. 기본·로딩·빈 상태·오류·비활성 상태는 U-04 상세 명세에서 정의한다.
프로토타입: `prototype/kitchen.html` (1920×1080 기준). 기준 기기: 주방 벽걸이·거치 모니터, 2m 거리, 장갑 낀 손.

## 구성
- 상단 바: 로고, 화면 이름, 실시간 연결 상태(아이콘 + 글자), 현재 시각.
- 두 레인: 접수(`received`) / 조리 중(`cooking`). 레인 제목에 건수.
- 주문 카드: 왼쪽 테이블 번호(72px)·경과 시간(32px), 오른쪽 메뉴명·수량(59px = 44pt), 하단 버튼 88px.
- 접수 카드 버튼 "조리 시작"(primary), 조리 중 카드 버튼 "조리 완료"(success). 항목이 끝났으면 "완료"를 아이콘 + 글자로 표시하고 이름을 `--color-text-secondary`로 낮춘다.
- 지연 표시(제안): 접수 후 10분 경과 시 카드 테두리 `--color-warning` + "지연" 배지(아이콘 + 글자). 기준 분은 사장님 확인 후 확정.
- 긴 메뉴명은 2줄까지 보이고 말줄임. 텍스트는 일반 텍스트로만 표시(D-24).

## 사용 토큰
`--font-size-kitchen-title/body/meta`, `--size-touch-kitchen`, `--color-warning`, `--color-success`, `--color-success-hover`, `--color-primary`, `--border-default`, 공용 Button·Badge·Card(U-03 components).

## 데이터 (openapi.yaml 기준)
- Order: `id`, `table_no`, `status`, `created_at`, `items[]`(`menu_name`, `qty`, `item_status`, `table_no`). 화면에는 `table_id` 대신 `table_no`를 보여 준다.
- 항목 단위 조리 처리: `PATCH /kitchen/items/{item_id}/status`(updateKitchenItemStatus).
- 경과 시간은 `created_at`에서 클라이언트가 계산한다.
- 갱신: `GET /stream/orders` (SSE).

## 계약 요청
없음. 민준 님 대조 결과 `table_no`와 항목 상태 변경 엔드포인트는 이미 계약에 있다. 이번 시안은 주문 단위 버튼만 두고, 항목 단위 처리 UI는 U-04 상세 명세에서 정한다.

## 대비
본문 `--color-text-primary` on 흰색 16.1:1, "지연" `--color-warning-text` on `--color-warning-light` 7.41:1, 흰 글자 on 버튼 5.13~5.75:1. 직접 계산한 값이며 도구 검증 전.

## 완료 조건 (구현자, U-04 상세 명세 전 잠정)
1. 메뉴명·수량 글자 59px 이상, 버튼 높이 88px 이상.
2. 상태는 색 + 아이콘 + 글자.
3. 토큰 변수만 사용. 하드코딩 색 없음.
