# Q-05 E2E 파일럿 시나리오

기준: D-30 파일럿(10/23), Playwright  
대상 브랜치: `feat/qa-q5` (F-04 머지 후 시작)  
실행 환경: 로컬 dev 서버 (`backend` + `frontend`) + PostgreSQL 18

---

## 공통 전제

- 시드 데이터: 메뉴A(재료X 2개 필요, 가격 10,000원), 재료X 재고 20개
- 테이블 t_1 존재, QR 토큰 발급 가능
- 직원 계정 `staff@pos.local` / 비밀번호 `staff1234`
- 사장 계정 `owner@pos.local` / 비밀번호 `owner1234`
- 주방 계정 `kitchen@pos.local` / 비밀번호 `kitchen1234`

---

## SC-01 QR 세션 진입

### 사전 조건
- t_1 테이블의 유효한 QR URL 준비 (예: `/customer?table_id=t_1&token=<valid>`)

### 진행 단계
1. QR URL 접속
2. `POST /tables/t_1/session` 요청 확인

### 기대 화면·API 결과
- 화면: 메뉴 목록 표시
- API: `POST /tables/t_1/session` → 200, tableToken 발급
- `GET /menus` → 200, 메뉴 목록 반환
- 화면에 `stock_warnings` 노출 없음

---

## SC-02 손님 주문

### 사전 조건
- SC-01 완료 (tableToken 보유)
- 재료X 재고 20개

### 진행 단계
1. 메뉴A 수량 2 선택 → 장바구니 추가
2. 주문 버튼 클릭
3. 주문 버튼 한 번 더 클릭 (중복 방지 확인)

### 기대 화면·API 결과
- API: `POST /orders` → 201, `Idempotency-Key` 포함, 동일 키 2회 요청 시 동일 order id 반환
- 화면: 주문 상태 `received` 표시
- DB: orders +1건, stock_movements(order_deduction) -4 (재료X 2개×2인분)
- 재료X 현재고: 16

---

## SC-03 주방 조리

### 사전 조건
- SC-02 완료 (주문 `received` 상태)
- 주방 계정 로그인

### 진행 단계
1. `/kitchen` 접속 → 주방 로그인
2. 큐에 SC-02 주문의 항목 표시 확인
3. 첫 번째 항목 "조리 시작" 버튼 클릭
4. 두 번째 항목 "조리 시작" → "조리 완료" 순서로 클릭

### 기대 화면·API 결과
- API: `GET /kitchen/queue` → 5초 이내 자동 갱신
- 첫 항목 "조리 시작": `PATCH /kitchen/items/{id}/status` `{"status":"cooking"}` → 200
- 주문 상태 DB: `cooking` 전이 (첫 항목 cooking 시)
- 두 번째 항목 완료 후 주문 상태 DB: `cooking` 유지 (served 자동 전이 없음)

---

## SC-04 서빙 (직원 수동)

### 사전 조건
- SC-03 완료 (모든 항목 `done`, 주문 `cooking`)
- 직원 계정 로그인

### 진행 단계
1. 직원 화면에서 해당 주문 조회
2. "서빙 완료" 버튼 클릭

### 기대 화면·API 결과
- API: `PATCH /orders/{order_id}/status` `{"status":"served"}` → 200
- DB: 주문 status = `served`
- 손님 화면 10초 폴링 후 상태 `served`로 갱신

---

## SC-05 결제 완료

### 사전 조건
- SC-04 완료 (주문 `served`)

### 진행 단계
1. 직원 화면에서 해당 주문 "결제 완료" 버튼 클릭

### 기대 화면·API 결과
- API: `PATCH /orders/{order_id}/status` `{"status":"paid"}` → 200
- DB: 주문 status = `paid`

---

## SC-06 조리 전 취소

### 사전 조건
- 신규 주문 생성 (항목 상태 모두 `pending`, 주문 `received`)
- 재료X 차감 후 현재고 16개 (재고 20개 기준 -4)
- 직원 계정 로그인

### 진행 단계
1. 직원 화면에서 해당 주문 "취소" 버튼 클릭

### 기대 화면·API 결과
- API: `PATCH /orders/{order_id}/status` `{"status":"cancelled"}` → 200
- DB: 주문 status = `cancelled`
- DB: stock_movements `cancel_restore` +4 추가
- DB: `disposal` 레코드 없음
- 재료X 현재고: 20 복원

---

## SC-07 조리 후 취소 (사장 전용)

### 사전 조건
- 신규 주문 생성 후 항목 중 하나 `cooking` 상태로 변경
- 재료X 현재고 16개
- 사장 계정 로그인

### 진행 단계
1. 사장 화면에서 해당 주문 "취소" 버튼 클릭

### 기대 화면·API 결과
- API: `PATCH /orders/{order_id}/status` `{"status":"cancelled"}` → 200
- DB: `cancel_restore` +4, `disposal` -4 한 쌍 추가
- 재료X 현재고: 16 유지 (순 변화 0, D-19)

---

## SC-08 직원 권한 403 (조리 후 취소 시도)

### 사전 조건
- SC-07 사전 조건과 동일 (항목 중 하나 `cooking`)
- 직원 계정 로그인

### 진행 단계
1. 직원 화면에서 해당 주문 "취소" 버튼 클릭

### 기대 화면·API 결과
- API: `PATCH /orders/{order_id}/status` `{"status":"cancelled"}` → **403**
- 화면: 에러 메시지 표시 ("조리 후 취소는 사장만 가능합니다")
- DB: 주문 상태 변화 없음 (`cooking` 유지)
- DB: 추가 stock_movements 없음

---

## 실행 순서 의존성

```
SC-01 → SC-02 → SC-03 → SC-04 → SC-05  (정상 흐름)
SC-01 → SC-02 → SC-06                   (조리 전 취소)
SC-01 → SC-02 → SC-03(일부) → SC-07     (사장 조리 후 취소)
SC-01 → SC-02 → SC-03(일부) → SC-08     (직원 권한 403)
```

각 시나리오는 독립 실행을 위해 `beforeEach`에서 DB를 시드 상태로 초기화한다.
