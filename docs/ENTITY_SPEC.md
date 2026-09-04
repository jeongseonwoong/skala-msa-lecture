# 모듈별 엔티티 필드 명세

> JPA 엔티티는 4개(user · course · enrollment · payment). recommend-service는 DB가 없어 무상태(Pydantic 스키마만 존재).
> 모든 엔티티 공통: `@GeneratedValue(IDENTITY)` PK, Spring Data Auditing(`createdAt` / `updatedAt`), 단일 스키마 `lecture_db` 공유.

---

## user-service — `users`

| 필드 | 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| id | `id` | Long | PK, auto | 식별자 |
| email | `email` | String | NOT NULL, UNIQUE | 로그인 이메일 |
| password | `password` | String | NOT NULL | 암호화된 비밀번호 |
| name | `name` | String | NOT NULL | 이름 |
| role | `role` | Enum(STRING) | NOT NULL | `MD` / `SELLER` / `BUYER` |
| sellerStatus | `seller_status` | Enum(STRING) | NULL 허용 | `ACTIVE` / `WARNING` / `TERMINATED` — SELLER 역할만 값 존재 |
| createdAt | `created_at` | LocalDateTime | updatable=false | 생성일시 |
| updatedAt | `updated_at` | LocalDateTime | — | 수정일시 |

**Enum**

- `Role` : `MD`(솔루션 운영자·로그인 유저) / `SELLER`(평가 대상 셀러) / `BUYER`(주문 발생 소비자)
- `SellerStatus` : `ACTIVE`(정상 입점) / `WARNING`(경고) / `TERMINATED`(퇴출)

---

## course-service — `courses` (상품 도메인)

| 필드 | 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| id | `id` | Long | PK, auto | 식별자 |
| title | `title` | String | NOT NULL | 상품명 |
| description | `description` | TEXT | — | 상세 설명 |
| category | `category` | Enum(STRING) | NOT NULL | 상품 카테고리 |
| price | `price` | BigDecimal(10,2) | NOT NULL | 가격 |
| instructorId | `instructor_id` | Long | NOT NULL | 셀러 ID (users 참조 — 직접 JOIN 없이 ID만 보관) |
| enrollmentCount | `enrollment_count` | Integer | NOT NULL, 기본 `0` | 누적 판매건수 (평가 서비스 판매량 지표) |
| status | `status` | Enum(STRING) | NOT NULL, 기본 `ACTIVE` | 노출 상태 |
| createdAt | `created_at` | LocalDateTime | updatable=false | 생성일시 |
| updatedAt | `updated_at` | LocalDateTime | — | 수정일시 |

**Enum**

- `Category` : `FASHION` / `BEAUTY` / `FOOD` / `DIGITAL` / `HOME` / `SPORTS` / `BOOK` / `OTHER`
- `Status` : `ACTIVE` / `INACTIVE`

**동작**

- `increaseEnrollmentCount()` : 수강(주문) 확정 시 `enrollmentCount + 1`

---

## enrollment-service — `enrollments` (주문 / 수강 도메인)

| 필드 | 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| id | `id` | Long | PK, auto | 식별자 |
| userId | `user_id` | Long | NOT NULL | 구매자 ID |
| courseId | `course_id` | Long | NOT NULL | 상품 ID |
| status | `status` | Enum(STRING) | NOT NULL, 기본 `PENDING` | 주문 상태 |
| createdAt | `created_at` | LocalDateTime | updatable=false | 주문 생성일시 |
| updatedAt | `updated_at` | LocalDateTime | — | 수정일시 |

> `(user_id, course_id)` 유니크 제약 **없음** — 한 구매자가 같은 상품을 여러 번 주문 가능.

**Enum**

- `Status` : `PENDING`(주문 생성·결제 대기) / `COMPLETED`(결제 완료된 정상 주문) / `CANCELLED`(취소) / `RETURNED`(반품)

**동작**

- `complete()` : 상태 → `COMPLETED`
- `cancel()` : 상태 → `CANCELLED`

---

## payment-service — `payments`

| 필드 | 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- | --- |
| id | `id` | Long | PK, auto | 식별자 |
| userId | `user_id` | Long | NOT NULL | 결제자 ID |
| courseId | `course_id` | Long | NOT NULL | 대상 상품 ID |
| amount | `amount` | BigDecimal(10,2) | NOT NULL | 결제 금액 |
| status | `status` | Enum(STRING) | NOT NULL, 기본 `PENDING` | 결제 상태 |
| transactionId | `transaction_id` | String | UNIQUE, NULL 허용 | 외부 PG사 거래 ID (실습에서는 UUID로 대체) |
| createdAt | `created_at` | LocalDateTime | updatable=false | 생성일시 |
| updatedAt | `updated_at` | LocalDateTime | — | 수정일시 |

**Enum**

- `Status` : `PENDING`(결제 대기) / `COMPLETED`(결제 완료) / `FAILED`(결제 실패) / `CANCELLED`(취소)

**동작**

- `complete(transactionId)` : 상태 → `COMPLETED`, 거래 ID 기록
- `fail()` : 상태 → `FAILED`

---

## recommend-service — DB 없음 (무상태)

엔티티 / 테이블이 없습니다. 매 요청마다 user · course · enrollment 서비스의 `/internal` API를 조회해 메모리에서 계산합니다.

| 스키마 | 성격 | 주요 필드 |
| --- | --- | --- |
| `SellerMetrics` | 내부 집계 지표 | `sellerId`, `sellerName`, `sellerStatus`, `category`, `salesCount30d`, `sales7d` / `salesPrev7d`, `cancelReturnCount`, `totalOrderCount`, `refundAmount`, `totalPaymentAmount`, `revenue30d`, `daysSinceLastOrder`, `newOrders14d`, `categoryAvgSales30d` |
| `SellerEvaluationOut` | API 응답 (프론트 계약) | `id`, `name`, `category`, `grade`(`EXCELLENT`/`WARNING`/`REVIEW`/`INSUFFICIENT`), `score`, `sellerStatus`, `joinedAt`, `metrics`(`MetricsOut`), `issues`(`IssueOut[]`), `insufficientNote` |
| `MetricsOut` | 응답 내 지표 블록 | `sales30d`, `categoryAvgSales30d`, `sales7d`, `salesPrev7d`, `cancelRate`, `refundRate`, `revenue30d`, `minRevenueThreshold`, `daysSinceLastOrder` |
| `IssueOut` | 응답 내 이슈 항목 | `type`, `severity`, `detail` |

> Kafka `enrollment.completed` 이벤트(`enrollmentId`, `userId`, `courseId`)도 소비하지만 현재는 로그만 남깁니다.
