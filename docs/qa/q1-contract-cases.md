# Q1 계약 테스트 케이스 명세

기준 결정: D-14~D-18 (2026-10-15)  
대상 엔드포인트: `POST /orders`, `POST /orders/{order_id}/status`, `POST /kitchen/items/{item_id}/status`

---

## TC-01 중복 키 동시 요청 (D-15)

**목적:** 같은 `Idempotency-Key`로 동시에 2건이 들어와도 주문 1건만 생성되고 재고는 1회만 차감된다.

### 사전 조건
- 메뉴 A: 레시피에 재료 X 2개 필요
- 재료 X 재고 10개
- `idempotency_keys` 테이블에 해당 키 없음

### 입력
```
POST /orders  (동시에 2번)
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440001
Authorization: tableToken <valid>

{
  "items": [{ "menu_id": "m_1", "quantity": 1 }]
}
```

### 기대 응답
- 두 요청 모두 `201 Created` 반환
- 두 응답의 `order.id` 동일
- `stock_warnings` 없음 (재고 충분)

### 기대 DB 상태
| 테이블 | 조건 |
|---|---|
| `orders` | 건수 +1 (중복 생성 없음) |
| `stock_movements` | reason=`order_deduction`, ingredient_id=X, quantity=-2 인 레코드 1건만 추가 |
| `idempotency_keys` | 해당 키 레코드 1건 존재 |

---

## TC-02 같은 키에 다른 본문 (D-15)

**목적:** 이미 사용된 `Idempotency-Key`로 본문이 다른 요청이 오면 422를 반환한다.

### 사전 조건
- TC-01 이후 상태(키 `550e8400-e29b-41d4-a716-446655440001` 이미 존재)

### 입력
```
POST /orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440001
Authorization: tableToken <valid>

{
  "items": [{ "menu_id": "m_2", "quantity": 3 }]
}
```

### 기대 응답
```json
HTTP 422 Unprocessable Entity
{
  "detail": "Idempotency-Key conflict: request body differs from original"
}
```

### 기대 DB 상태
| 테이블 | 조건 |
|---|---|
| `orders` | 건수 변화 없음 |
| `stock_movements` | 추가 레코드 없음 |

---

## TC-03 조리 전 취소 — 재고 복원 (D-16, D-06)

**목적:** 주문 상태가 `received` 일 때 취소하면 재고가 복원된다.

### 사전 조건
- 주문 `o_1` 상태: `received`
- 모든 항목 상태: `pending`
- 재고: 재료 X = 8 (주문 생성 시 2 차감된 상태)
- 취소 요청자: 직원(staff) 또는 사장(owner)

### 입력
```
POST /orders/o_1/status
Authorization: Bearer <staff_token 또는 owner_token>

{ "status": "cancelled" }
```

### 기대 응답
```json
HTTP 200 OK
{ "order_id": "o_1", "status": "cancelled" }
```

### 기대 DB 상태
| 테이블 | 조건 |
|---|---|
| `orders` | `o_1` status = `cancelled` |
| `stock_movements` | reason=`cancel_restore`, ingredient_id=X, quantity=+2 레코드 추가 |
| 재료 X 현재고 | 10 복원 |

---

## TC-04 조리 후 취소 — 재고 복원 없음, 폐기 기록 (D-16, D-06)

**목적:** 주문이 `cooking` 이상일 때 취소하면 재고는 복원하지 않고 `stock_movements`에 폐기 기록이 남는다.

### 사전 조건
- 주문 `o_2` 상태: `cooking`
- 적어도 하나의 항목 상태: `cooking` 또는 `done`
- 재고: 재료 X = 8 (주문 생성 시 2 차감된 상태)
- 취소 요청자: 사장(owner)

### 입력
```
POST /orders/o_2/status
Authorization: Bearer <owner_token>

{ "status": "cancelled" }
```

### 기대 응답
```json
HTTP 200 OK
{ "order_id": "o_2", "status": "cancelled" }
```

### 기대 DB 상태
| 테이블 | 조건 |
|---|---|
| `orders` | `o_2` status = `cancelled` |
| `stock_movements` | reason=`disposal`, ingredient_id=X, quantity=-2 레코드 추가 (복원 레코드 없음) |
| 재료 X 현재고 | 8 유지 (변화 없음) |

---

## TC-05 직원의 조리 후 취소 시도 — 403 (D-16, D-06)

**목적:** 직원이 `cooking` 이상인 주문을 취소 시도하면 403을 반환한다.

### 사전 조건
- 주문 `o_2` 상태: `cooking`
- 취소 요청자: 직원(staff)

### 입력
```
POST /orders/o_2/status
Authorization: Bearer <staff_token>

{ "status": "cancelled" }
```

### 기대 응답
```json
HTTP 403 Forbidden
{
  "detail": "조리 후 취소는 사장만 가능합니다"
}
```

### 기대 DB 상태
| 테이블 | 조건 |
|---|---|
| `orders` | `o_2` status 변화 없음 (`cooking` 유지) |
| `stock_movements` | 추가 레코드 없음 |

---

## TC-06 항목 상태 변경에 따른 주문 자동 전이 (D-16)

**목적:** 항목 상태 변경 시 주문 상태가 서비스 레이어에서 같은 트랜잭션 내에 자동으로 계산된다.

### 사전 조건
- 주문 `o_3` 상태: `received`, 항목 2개(i_1, i_2) 모두 `pending`

### 시나리오 A — 첫 번째 항목 조리 시작 → 주문 `cooking` 전이

**입력**
```
POST /kitchen/items/i_1/status
Authorization: Bearer <kitchen_token>

{ "status": "cooking" }
```

**기대 응답**
```json
HTTP 200 OK
{ "item_id": "i_1", "status": "cooking" }
```

**기대 DB 상태**
| 테이블 | 조건 |
|---|---|
| `order_items` | i_1 status = `cooking`, i_2 status = `pending` |
| `orders` | `o_3` status = `cooking` |

### 시나리오 B — 모든 항목 완료 → 주문 자동 전이 검증

**입력 (순서대로)**
1. `POST /kitchen/items/i_1/status` → `{ "status": "done" }`
2. `POST /kitchen/items/i_2/status` → `{ "status": "done" }`

**기대 DB 상태 (2번 요청 후)**
| 테이블 | 조건 |
|---|---|
| `order_items` | i_1, i_2 모두 status = `done` |
| `orders` | `o_3` status = `cooking` 유지 (`served`는 직원 수동 처리) |

> `served` 전이는 직원이 `POST /orders/o_3/status { "status": "served" }`로 수동 처리.

---

## TC-07 재고 부족 시 주문 생성 — 201 + stock_warnings (D-14)

**목적:** 재료가 부족해도 주문은 201로 생성되고, 응답에 `stock_warnings[]`가 포함된다.

### 사전 조건
- 메뉴 B: 레시피에 재료 Y 5개 필요
- 재료 Y 현재고: 3개 (부족)

### 입력
```
POST /orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440002
Authorization: tableToken <valid>

{
  "items": [{ "menu_id": "m_B", "quantity": 1 }]
}
```

### 기대 응답
```json
HTTP 201 Created
{
  "order_id": "o_new",
  "status": "received",
  "stock_warnings": [
    {
      "ingredient_id": "ing_Y",
      "current_stock": 3,
      "required_quantity": 5
    }
  ]
}
```

### 기대 DB 상태
| 테이블 | 조건 |
|---|---|
| `orders` | 건수 +1, status = `received` |
| `stock_movements` | reason=`order_deduction`, ingredient_id=Y, quantity=-5 레코드 추가 (음수 재고 허용, D-07) |

### SSE 이벤트 검증
- 직원/사장 SSE 구독 채널에 `stock.warning` 이벤트 발생
- 이벤트 data에 `ingredient_id`, `current_stock`, `required_quantity` 포함

---

## 공통 주의 사항

- 모든 TC에서 `Idempotency-Key`는 UUID v4 형식이어야 한다.
- 상태 전이는 영문 enum(D-18): 주문 `received`/`cooking`/`served`/`paid`/`cancelled`, 항목 `pending`/`cooking`/`done`.
- 취소 상태 전이 엔드포인트: `POST /orders/{order_id}/status` (PATCH 아님).
- DB 상태 검증은 SEED=42 고정 테스트 데이터 기준으로 한다(D-12).
- TC-03~TC-05는 조리 단계 판단 기준이 "항목 상태에 `cooking` 또는 `done`이 하나라도 있는가"임을 주의한다.
