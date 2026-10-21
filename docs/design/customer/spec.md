# U-06 손님 QR 주문 화면 명세 (시안 단계, U-03)

상태: 메뉴 목록 메인 화면 시안만. 장바구니·주문 확인·주문 상태, 그리고 기본·로딩·빈 상태·오류·비활성 상태는 U-06 상세 명세에서 정의한다.
프로토타입: `prototype/customer.html` (390×844 모바일 기준, 최대 480px). 기준 기기: 손님 휴대폰, 한 손 조작.

## 구성
- 상단 바: 로고, 테이블 번호 배지, 탭(메뉴 / 주문 내역, 높이 48px).
- 카테고리 칩(가로 스크롤, 높이 44px). 카테고리는 `Menu.category`.
- 메뉴 행 카드: 이름(2줄 말줄임), 가격, 오른쪽에 "담기" 버튼 또는 수량 조절(− 수량 +, 각 44px). 담으면 수량 조절로 바뀐다.
- 하단 고정 바: "장바구니 보기" + 담은 개수 + 합계. 장바구니가 비면 비활성.
- 엄지 영역(화면 아래쪽)에 주 행동을 둔다. 메뉴 이름은 일반 텍스트로만 표시한다.

## 사용 토큰
`--size-phone-max`, `--size-touch-lg`(하단 바 52px 이상), `--size-touch-min`, `--color-primary`, 공용 Button·Card·Badge(U-03 components).

## 데이터 (openapi.yaml 기준)
- Menu: `id`, `name`, `price`, `category`, `is_active`. 목록은 `GET /menus`(tableToken).
- 주문 생성 본문은 `items[{menu_id, qty}]`만 보낸다. 세션은 `POST /tables/{table_id}/session`.

## 계약 요청 (민준 님께)
1. 테이블 번호 표시: 세션 응답에 `table_no`가 없다(`table_session_token`, `expires_at`만 있음).
2. 일시 품절(D-37)을 손님에게 "품절"로 보여 줄지, 목록에서 빼는지 결정이 필요하다. 현재 Menu에는 `is_active`뿐이고 손님 목록이 비활성 메뉴를 돌려주는지도 명시돼 있지 않다.
3. `stock_warnings[]`는 손님 화면에 노출하지 않는다. 손님 응답에서 빼 줄 수 있는지 확인이 필요하다.
4. 메뉴 이미지·설명 필드는 없다. 이번 시안은 이름·가격만 쓴다.

## 대비
`--color-text-secondary` on 흰색 5.74:1(가격), `--color-primary` on `--color-info-light` 5.03:1(선택 칩), 흰 글자 on primary 5.75:1. 직접 계산한 값이며 도구 검증 전.

## 완료 조건 (구현자, 잠정)
1. 320px 폭에서 가로 스크롤 없이 동작(카테고리 칩 제외).
2. 모든 터치 요소 44px 이상. 하단 바에 안전 영역(`env(safe-area-inset-bottom)`) 반영.
3. 토큰 변수만 사용.
