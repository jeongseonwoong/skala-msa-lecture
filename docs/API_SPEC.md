# 상품 이슈 모니터링 API 명세서

> **Sprint 1 · 프론트엔드 계약서**
> 이커머스 셀러가 상품을 등록하고, 모니터링 대상으로 지정하고, 매일 아침 운영 데이터를 올려
> "오늘 볼 상품"을 받아보는 흐름의 전체 엔드포인트.

| 항목 | 값 |
| --- | --- |
| Gateway | `http://localhost:8080` (프론트 `VITE_API_BASE_URL`) |
| 대상 서비스 | course-service · enrollment-service · recommend-service |
| 최종 수정 | 2026-09-03 |
| 상태 | **구현 예정 계약** — 백엔드 코드는 아직 변경 전 |

---

## 목차

1. [호출 규약 · 인증](#1-호출-규약--인증)
2. [에러 응답](#2-에러-응답)
3. [Enum 사전](#3-enum-사전)
4. [상품 카탈로그 (course-service)](#4-상품-카탈로그-course-service)
5. [모니터링 · 지표 접수 (enrollment-service)](#5-모니터링--지표-접수-enrollment-service)
6. [CSV 파일 규격](#6-csv-파일-규격)
7. [이슈 분석 (recommend-service)](#7-이슈-분석-recommend-service)
8. [이슈 유형 8종 · 권장 액션](#8-이슈-유형-8종--권장-액션)
9. [인증 (user-service, 변경 없음)](#9-인증-user-service-변경-없음)
10. [변경 대조표](#10-변경-대조표)

---

## 1. 호출 규약 · 인증

프론트는 항상 **API Gateway(`:8080`) 한 곳만** 호출합니다. 서비스 포트(8082, 8083, 8085)를 직접 부르지 않습니다.

### 사용자 ID는 보내지 않습니다

모든 개인화 API는 게이트웨이가 JWT에서 꺼낸 `X-User-Id` 헤더를 백엔드에 주입합니다.
프론트는 `Authorization: Bearer <accessToken>`만 실으면 되고, 바디나 쿼리에 `userId`를 넣을 필요가 없습니다.
기존 `src/api/index.js`의 axios 인터셉터가 이미 이 토큰을 붙이고 있으므로 **추가 작업 없음**.

### 공통 응답 래퍼

Java 서비스(**course**, **enrollment**)는 모든 응답을 아래 래퍼로 감쌉니다. 실제 데이터는 `data` 안에 있습니다.

```json
{
  "success": true,
  "message": "성공",
  "data": {}
}
```

> ### ⚠️ 주의 — recommend-service는 래퍼가 없습니다
>
> 이슈 분석 API는 FastAPI로 작성돼 있어 `{success, message, data}` 래퍼 **없이** 결과 객체를 그대로 반환합니다.
> `res.data.data`가 아니라 **`res.data`를 바로** 쓰세요.

---

## 2. 에러 응답

Java 서비스의 `GlobalExceptionHandler`가 처리하는 실제 응답 형태입니다.

| 상태 | 발생 상황 | `message` 예시 |
| --- | --- | --- |
| `400` | 검증 실패(`@Valid`) — 필드 메시지를 쉼표로 이어붙임 | `상품명은 필수입니다, 원가는 0 이상이어야 합니다` |
| `400` | 비즈니스 규칙 위반(`IllegalArgumentException`) | `이미 모니터링 중인 상품입니다` |
| `401` | 토큰 없음 / 만료 | 게이트웨이가 반환 — 바디 형식 다름 |
| `500` | 그 외 모든 예외 (원인 메시지 비노출) | `서버 오류가 발생했습니다` |

```json
{
  "success": false,
  "message": "이미 모니터링 중인 상품입니다",
  "data": null
}
```

> **없는 리소스는 404가 아니라 400입니다.** `IllegalArgumentException`으로 처리되기 때문입니다.

---

## 3. Enum 사전

API는 **영문 코드값만** 주고받습니다. 화면 표기용 한글 라벨은 프론트에서 매핑하세요.

### Category — 상품 카테고리

| 코드 | 라벨(제안) |
| --- | --- |
| `FASHION` | 패션의류·잡화 |
| `BEAUTY` | 뷰티 |
| `FOOD` | 식품 |
| `LIVING` | 리빙·주방 |
| `DIGITAL` | 디지털·가전 |
| `SPORTS` | 스포츠·레저 |
| `KIDS` | 유아동 |
| `OTHER` | 기타 |

### Season — 시즌 속성

`SPRING` · `SUMMER` · `FALL` · `WINTER` · `ALL`

### Status — 상품 판매 상태

| 코드 | 의미 |
| --- | --- |
| `ACTIVE` | 판매중 (목록 노출 대상) |
| `INACTIVE` | 판매중지 |

### MonitorStatus — 모니터링 상태

| 코드 | 의미 |
| --- | --- |
| `DETECTED` | 모니터링 등록됨, 분석 대기 |
| `ACTIVE` | 분석 활성 — 이슈 리포트 대상 |
| `CANCELLED` | 모니터링 해제 |

> **Sprint 1 한정** — 구독 결제가 없으므로 모니터링 지정 즉시 `ACTIVE`로 저장됩니다.
> `DETECTED`는 Sprint 2에서 `payment.completed` 이벤트를 받기 전 상태로 쓰입니다.
> 프론트는 지금부터 세 값을 모두 처리할 수 있게 뱃지를 만들어 두세요.

---

## 4. 상품 카탈로그 (course-service)

경로는 기존 `/api/courses`를 그대로 씁니다. **필드 구성이 커머스 상품으로 바뀝니다.**

### 4.1 `POST /api/courses` — 상품 등록 `[필드 변경]`

셀러가 판매 상품을 카탈로그에 등록합니다. 등록자(`sellerId`)는 토큰에서 자동 결정됩니다.
성공 시 **201 Created**.

#### Request body

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| `sku` | string | ✅ | 상품 코드. 전체 유일. **CSV 업로드의 매칭 키**이므로 셀러가 실제 쓰는 코드를 넣어야 함 |
| `title` | string | ✅ | 상품명 |
| `description` | string | — | 상품 설명 |
| `category` | Category | ✅ | Enum 사전 참고 |
| `price` | number | ✅ | 현재 판매가(원). 0 이상 |
| `listPrice` | number | ✅ | 정상가(원). 할인율 표시에 사용 |
| `cost` | number | ✅ | 원가(원). `MARGIN_LOW` 판정 기준 |
| `season` | Season | — | 미전송 시 `ALL` |
| `seasonEndDate` | string | — | `YYYY-MM-DD`. `SEASON_END_RISK` 판정에 필요 — `season`이 `ALL`이 아니면 함께 전송 |
| `targetMarginRate` | number | — | 목표 마진율. 비율 0~1 (예: `0.25`). 미전송 시 `0.20` |

#### 요청 예시

```json
{
  "sku": "LN-SHIRT-OV-01",
  "title": "린넨 오버셔츠",
  "description": "프렌치 린넨 100%, 3color",
  "category": "FASHION",
  "price": 39000,
  "listPrice": 49000,
  "cost": 17800,
  "season": "SUMMER",
  "seasonEndDate": "2026-09-20",
  "targetMarginRate": 0.25
}
```

#### 201 응답 — `data`

```json
{
  "id": 128,
  "sku": "LN-SHIRT-OV-01",
  "title": "린넨 오버셔츠",
  "description": "프렌치 린넨 100%, 3color",
  "category": "FASHION",
  "price": 39000.00,
  "listPrice": 49000.00,
  "cost": 17800.00,
  "season": "SUMMER",
  "seasonEndDate": "2026-09-20",
  "targetMarginRate": 0.2500,
  "sellerId": 7,
  "watchCount": 0,
  "status": "ACTIVE",
  "createdAt": "2026-09-03T08:14:22.481"
}
```

> **이름이 바뀌는 두 필드**
> `instructorId` → `sellerId`, `enrollmentCount` → `watchCount`.
> 현재 `CourseCard.vue`와 `MyPageView.vue`가 옛 이름을 읽고 있으니 함께 고쳐야 합니다.
> `watchCount`는 "이 상품을 모니터링 중인 셀러 수"라서 카드에 굳이 노출하지 않아도 됩니다.

---

### 4.2 `GET /api/courses` — 판매중 상품 목록 `[경로 유지]`

`status = ACTIVE`인 상품 전체를 배열로 반환합니다.
페이징·검색 파라미터는 Sprint 1 범위 밖 — 기존 `courseApi.getCourses(params)`가 넘기던 `params`는 **무시**됩니다.

```json
{
  "success": true,
  "message": "성공",
  "data": [ /* 4.1의 상품 객체와 동일한 형태 × N */ ]
}
```

---

### 4.3 `GET /api/courses/{id}` — 상품 상세 `[경로 유지]`

| 파라미터 | 위치 | 설명 |
| --- | --- | --- |
| `id` | path | 상품 PK (`sku` 아님) |

없으면 **400** + `"상품을 찾을 수 없습니다: 128"`.

---

### 4.4 `GET /api/courses/category/{category}` — 카테고리별 상품 `[경로 유지]`

해당 카테고리의 판매중 상품만 반환합니다.
`{category}`는 `FASHION` 같은 **Enum 코드값 그대로** 넣습니다 (한글 라벨 아님).

---

## 5. 모니터링 · 지표 접수 (enrollment-service)

경로는 기존 `/api/enrollments`를 유지합니다. "수강"이 "모니터링 지정"으로 바뀌고, CSV 업로드가 추가됩니다.

### 5.1 `POST /api/enrollments` — 모니터링 대상 지정 `[동작 변경]`

상품을 내 모니터링 목록에 추가합니다.
**Sprint 1에서는 결제 호출이 사라집니다** — 기존처럼 결제 대기(`PENDING`)로 남지 않고 바로 분석 대상이 됩니다.
성공 시 **201 Created**.

#### 요청 — 바디 그대로 유지

```json
{ "courseId": 128 }
```

#### 201 응답 — `data`

```json
{
  "id": 41,
  "userId": 7,
  "courseId": 128,
  "monitorStatus": "ACTIVE",
  "issueSummary": null,
  "priorityScore": null,
  "createdAt": "2026-09-03T08:20:11.902",
  "product": null
}
```

#### 실패 케이스 (400)

| 상황 | message |
| --- | --- |
| 존재하지 않는 상품 | `존재하지 않는 상품입니다: 128` |
| 중복 지정 | `이미 모니터링 중인 상품입니다` |

> **필드명 변경**
> 응답의 `status`가 `monitorStatus`로 바뀌고 값 집합도 달라집니다(`PENDING` 없음).
> `issueSummary`·`priorityScore`는 Sprint 1에서 **항상 `null`**이며 Sprint 2 선계산 이후 채워집니다 —
> 프론트는 `null`을 정상 상태로 처리하세요.

---

### 5.2 `GET /api/enrollments/my` — 내 모니터링 목록 `[필드 변경]`

내가 지정한 모니터링 상품 전체. 각 항목에 `product`로 상품 요약이 붙어 오므로 **상품 상세를 따로 호출할 필요가 없습니다.**

#### 200 응답 — `data` 배열 항목

```json
{
  "id": 41,
  "userId": 7,
  "courseId": 128,
  "monitorStatus": "ACTIVE",
  "issueSummary": null,
  "priorityScore": null,
  "createdAt": "2026-09-01T09:12:04.113",
  "product": {
    "id": 128,
    "sku": "LN-SHIRT-OV-01",
    "title": "린넨 오버셔츠",
    "category": "FASHION",
    "price": 39000.00,
    "listPrice": 49000.00,
    "cost": 17800.00,
    "season": "SUMMER",
    "status": "ACTIVE"
  }
}
```

기존 `CourseSummary`에 있던 `thumbnail`·`instructorName`·`enrollmentCount`는 **없어집니다**.
카테고리는 **영문 코드**로 옵니다 — 서버가 한글로 변환해 주던 동작(`normalizeCategory`)이 사라지니 프론트에서 매핑하세요.

---

### 5.3 `GET /api/enrollments/user/{userId}` — 특정 사용자 모니터링 목록 `[경로 유지]`

응답 형태는 5.2와 동일합니다. 관리/디버깅용.

---

### 5.4 `POST /api/enrollments/metrics/upload` — 일일 운영 데이터 CSV 업로드 `[신규]`

아침에 채널·ERP에서 내려받은 지표 CSV를 통째로 올립니다.
**내가 모니터링 중인 상품의 행만** 저장되고, 나머지는 건너뜁니다.

| 항목 | 값 |
| --- | --- |
| Content-Type | `multipart/form-data` — axios에 직접 지정하지 말고 `FormData`를 넘겨 브라우저가 boundary를 붙이게 둘 것 |
| 파트 이름 | `file` |
| 인코딩 | UTF-8 (BOM 허용) |
| 중복 업로드 | 같은 `(상품, metric_date)` 조합은 덮어씀 — 하루에 여러 번 올려도 안전 |

#### 호출 예시

```js
const form = new FormData()
form.append('file', csvFile)

api.post(
  '/api/enrollments/metrics/upload',
  form,
  { headers: { 'Content-Type': undefined } }
)
```

#### 200 응답 — `data`

```json
{
  "uploadedRows": 48,
  "updatedRows": 12,
  "skippedRows": 2,
  "errors": [
    "3행: sku 'XX-999'에 해당하는 모니터링 상품이 없습니다",
    "17행: current_stock 값이 숫자가 아닙니다"
  ]
}
```

일부 행이 실패해도 **200**입니다.
`errors` 배열이 비어 있지 않으면 화면에 "48건 반영 · 2건 건너뜀" 식으로 요약하고 상세는 접어 두는 편이 좋습니다.

---

## 6. CSV 파일 규격

첫 줄은 반드시 헤더입니다. **컬럼 순서는 자유**이고 이름으로 매칭합니다.
빈 값은 `null`로 저장되며, 해당 지표를 쓰는 이슈 규칙만 건너뜁니다.

| 컬럼 | 타입 | 필수 | 설명 · 쓰이는 규칙 |
| --- | --- | --- | --- |
| `sku` | string | ✅ | 상품 매칭 키 |
| `metric_date` | date | ✅ | `YYYY-MM-DD` — 기준일 |
| `current_stock` | int | ✅ | 현재고 → `STOCKOUT_RISK`, `OVERSTOCK` |
| `sales_3d` | int | — | 최근 3일 판매 수량 → `SALES_DROP` |
| `sales_7d` | int | ✅ | 최근 7일 판매 수량 → 일평균 산출의 기준 |
| `sales_14d` | int | — | 최근 14일 판매 수량 → `SALES_DROP` |
| `order_count` | int | — | 최근 주문 건수 — 반품률 분모 |
| `return_count` | int | — | 최근 반품 건수 → `RETURN_SPIKE` |
| `review_avg_30d` | decimal | — | 최근 30일 평균 별점(0~5) → `REVIEW_DROP` |
| `review_avg_prev` | decimal | — | 직전 구간 평균 별점 → `REVIEW_DROP` 하락폭 |
| `competitor_min_price` | decimal | — | 경쟁사 최저가 → `PRICE_UNCOMPETITIVE` |
| `selling_price` | decimal | — | 업로드 시점 실판매가. 비우면 카탈로그의 `price` 사용 |
| `cost` | decimal | — | 업로드 시점 원가. 비우면 카탈로그의 `cost` 사용 |

### 샘플 (다운로드 템플릿으로 그대로 제공 가능)

```csv
sku,metric_date,current_stock,sales_3d,sales_7d,sales_14d,order_count,return_count,review_avg_30d,review_avg_prev,competitor_min_price,selling_price,cost
LN-SHIRT-OV-01,2026-09-03,24,18,60,140,142,9,4.1,4.3,35900,39000,17800
BT-SERUM-30,2026-09-03,880,4,11,38,40,1,4.6,4.5,28000,32000,9400
KD-SOCKS-5P,2026-09-03,52,0,3,26,27,6,3.2,3.9,7900,8900,3100
```

---

## 7. 이슈 분석 (recommend-service)

데모의 핵심 화면. **호출 시점에 규칙을 즉석 계산**하므로 사전 저장이나 폴링이 없습니다.

### 7.1 `GET /api/recommend/issues/{userId}` — 오늘 볼 상품 `[신규]`

해당 셀러의 모니터링 상품 전체를 훑어 이슈가 잡힌 상품만 **우선순위 내림차순**으로 반환합니다.
이슈가 하나도 없으면 `items`는 빈 배열입니다.

> **응답 래퍼 없음**
> 이 엔드포인트만 `{success, message, data}`로 감싸지 않고 아래 객체를 그대로 돌려줍니다.
> 기존 `GET /api/recommend/{userId}`(강의 추천)는 **없어집니다**.

#### 200 응답 (전체)

```json
{
  "userId": 7,
  "generatedAt": "2026-09-03T08:03:11",
  "metricDate": "2026-09-03",
  "totalWatched": 50,
  "items": [
    {
      "productId": 128,
      "sku": "LN-SHIRT-OV-01",
      "title": "린넨 오버셔츠",
      "category": "FASHION",
      "priorityScore": 0.842,
      "issues": [
        {
          "type": "STOCKOUT_RISK",
          "grade": "HIGH",
          "severity": 0.91,
          "evidence": "현재고 24개 ÷ 일평균 8.6개 = 2.8일분 (임계 5일)",
          "recommendedAction": "RESTOCK"
        },
        {
          "type": "RETURN_SPIKE",
          "grade": "MID",
          "severity": 0.42,
          "evidence": "반품률 6.3% (패션 평균 4.0% × 1.5 = 6.0%)",
          "recommendedAction": "INSPECT_QUALITY"
        }
      ]
    }
  ]
}
```

#### 필드 설명

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `metricDate` | date | 계산에 사용한 지표 기준일. 오늘 CSV를 안 올렸으면 마지막 업로드 날짜가 옴 — 화면에 "9월 1일 데이터 기준"처럼 노출 |
| `totalWatched` | int | 모니터링 총 상품 수. "50개 중 12개에 이슈" 문구용 |
| `priorityScore` | decimal | Σ(이슈 심각도 × 매출 기여도 가중치). **정렬 기준**이며 절대적 의미는 없음 |
| `severity` | decimal | 0~1로 정규화한 임계값 초과 비율 |
| `grade` | string | `HIGH` ≥ 0.7 · `MID` ≥ 0.4 · `LOW` — **뱃지 색상 분기에 이 값을 사용** |
| `evidence` | string | 완성된 한글 문장. 프론트에서 조합하지 말고 그대로 출력 |

---

## 8. 이슈 유형 8종 · 권장 액션

| type | 발동 조건 | recommendedAction | 화면 라벨 |
| --- | --- | --- | --- |
| `STOCKOUT_RISK` | 현재고 ÷ 7일 일평균 판매 < 5일 | `RESTOCK` | 재입고 |
| `SALES_DROP` | 3일 판매 ÷ 14일 평균 < 0.6 | `ADJUST_AD` | 광고 조정 |
| `RETURN_SPIKE` | 반품률 > 카테고리 평균 × 1.5 | `INSPECT_QUALITY` | 품질 점검 |
| `OVERSTOCK` | 현재고 ÷ 일평균 판매 > 60일 | `DISCOUNT` | 할인 |
| `REVIEW_DROP` | 30일 평균 별점 < 3.0 또는 직전 대비 −0.5 | `INSPECT_QUALITY` | 품질 점검 |
| `PRICE_UNCOMPETITIVE` | 최저가 아님 & 경쟁 최저가 대비 +10% 이상 | `REVIEW_PRICE` | 가격 검토 |
| `SEASON_END_RISK` | 시즌 종료 임박 & sell-through < 목표 | `DISCOUNT` | 할인 |
| `MARGIN_LOW` | (판매가 − 원가) ÷ 판매가 < 목표 마진율 | `REVIEW_PRICE` | 가격 검토 |

한 상품에 **여러 이슈가 동시에** 붙을 수 있습니다.
`issues`는 `severity` 내림차순으로 정렬돼 오므로, 카드에는 첫 번째 이슈를 대표 태그로 크게 보여주고 나머지는 `+2` 형태로 접어 두는 구성이 잘 맞습니다.

---

## 9. 인증 (user-service, 변경 없음)

기존 OAuth2 흐름 그대로입니다. 참고용.

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| `POST` | `/oauth2/token` | Authorization Code → Access Token 교환. `Basic` 헤더에 client 자격 증명 |
| `GET` | `/api/users/me` | 내 정보 — 셀러 `id`를 여기서 얻어 이슈 분석 API의 `{userId}`로 사용 |
| `POST` | `/api/users/register` | 회원가입 |

---

## 10. 변경 대조표

현재 `vue-frontend` 코드에서 손봐야 할 지점만 추렸습니다.

| 기존 | 변경 후 | 영향 받는 파일 |
| --- | --- | --- |
| `course.instructorId` | `course.sellerId` | `MyPageView.vue` |
| `course.enrollmentCount` | `course.watchCount` | `CourseCard.vue`, `CourseDetailView.vue`, `MyPageView.vue` |
| `enrollment.status` | `enrollment.monitorStatus` | 상태 뱃지 전반 |
| `PENDING` 상태 | 없어짐 → `DETECTED` | 상태 뱃지 매핑 |
| `enrollment.course` | `enrollment.product` | `MyPageView.vue` |
| 카테고리 한글 응답 | 영문 Enum 코드 | 프론트 라벨 매핑 추가 필요 |
| `GET /api/recommend/{userId}` | `GET /api/recommend/issues/{userId}` | `api/enrollment.js`의 `getRecommendations` |
| `DELETE /api/enrollments/{id}` | Sprint 1 미구현 — 호출하면 **404** | `api/enrollment.js`의 `cancel` |
| `PUT /api/courses/{id}` | Sprint 1 미구현 — 호출하면 **404** | `api/course.js`의 `update` |

---

## Sprint 2 예정 (참고)

- 월 구독 결제 (payment-service)
- `PATCH /api/enrollments/{id}/status` — 이슈 처리 상태(확인 / 조치중 / 해결)
- `payment.completed` Kafka 이벤트 → `DETECTED` → `ACTIVE` 자동 전환
- 이슈 리포트 백그라운드 선계산 → `issueSummary`·`priorityScore` 채워짐
