# 이커머스 리테일팀 운영 평가 솔루션

> SKALA 4반 3조 · Agile 방법론 및 MSA 개발 실습
> 원본 온라인 강의 플랫폼 템플릿을 **이커머스 셀러 운영 평가** 도메인으로 재해석한 프로젝트.
>
> 원 템플릿 저작권: For contact `audit@korea.ac.kr`, Sungryel Lim Ph.D
> (교육용 코드이며 상용 서비스로 쓰려면 배포 목적에 맞는 보완이 필요합니다.)

---

## 1. 이해관계자와 Pain Point

**고객 = 이커머스 플랫폼사의 「리테일팀(MD 조직)」**

개별 MD 한 사람이 아니라, 입점 셀러 관리를 책임지는 **부서 전체**가 이 서비스의 사용자다. MD는 이 부서에 속한 담당자로서 서비스에 로그인한다.

### 부서가 겪는 문제

- 부서가 관리하는 입점 셀러가 수백~수천 명. 셀러마다 판매량·취소율·환불율·매출·주문 추이를 **여러 화면에서 따로** 확인해야 한다.
- "지금 조치가 필요한 셀러가 누구인가"를 담당자마다 **다른 기준**으로 판단한다. 부서 차원의 일관된 평가 기준·우선순위가 없다.
- 그 결과 부실 셀러는 늦게 발견되고(악성 재고·CS 폭증·브랜드 훼손), 우량 셀러는 관리에서 소외된다.
- 신규 MD가 들어오면 "무엇을, 어떤 기준으로 봐야 하는지" 암묵지가 전수되지 않는다.

### 왜 Agile · MSA인가

- 평가 기준(임계값·가중치·규칙)은 **계속 바뀐다.** 규칙을 분리해 두고 스프린트마다 조정 → Agile.
- 회원·상품·주문·결제·평가는 **데이터 생성 단위가 다르다.** 서비스로 분리해 평가 로직만 독립적으로 교체 가능 → MSA. (Sprint 3에서 규칙 → ML 교체 예정)

---

## 2. AI 솔루션

**규칙 기반 셀러 운영 평가 엔진** (`recommend-service`)

- 입력: 셀러 목록(user-service) + 셀러별 상품(course-service) + 셀러별 주문 이력(enrollment-service)
- 처리: 원시 주문을 집계 지표로 변환 → **6개 규칙**으로 이슈 판정 → 종합점수·등급 산출
- 출력: **부서가 먼저 봐야 할 순서**로 정렬된 셀러 랭킹 + 셀러별 이슈·근거

AI 모델은 아직 쓰지 않고 규칙 기반이다. 규칙 기준선을 검증한 뒤 Sprint 3에서 이상탐지·예측 ML로 고도화한다.

### 6개 평가 규칙

| 규칙 | "문제" 판정 조건 | 가중치 |
| --- | --- | --- |
| `HIGH_CANCEL_RATE` (취소·반품 과다) | (취소+반품) ÷ 전체 주문 > 15% | 25 |
| `HIGH_REFUND_RATE` (환불 과다) | 환불액 ÷ 결제액 > 10% | 20 |
| `LOW_SALES` (판매 부진) | 30일 판매량 ÷ 카테고리 평균 < 0.5 | 15 |
| `SALES_DECLINING` (판매 급감) | 최근 7일 ÷ 이전 7일 < 0.7 | 15 |
| `LOW_REVENUE` (매출 미달) | 30일 매출 < 카테고리별 최소 기준액 | 15 |
| `NO_RECENT_ORDER` (주문 끊김) | 최근 14일간 신규 주문 0건 | 10 |

- **종합점수 = 100 − Σ(이슈 심각도(0~1) × 가중치)**, 0~100 clamp
- 등급: `80↑` 우수(EXCELLENT) / `50~79` 주의(WARNING) / `50 미만` 퇴출검토(REVIEW) / 누적 주문 5건 미만 평가보류(INSUFFICIENT)
- 임계값·가중치·카테고리 기준액은 전부 `recommend-service/app/rules/thresholds.py` 상수

---

## 3. 도메인 재해석 (테이블·컬럼명은 그대로, 의미만 변경)

| 원본 테이블 | 새 의미 | 주요 매핑 |
| --- | --- | --- |
| `users` | 회원 (`role`: `MD` / `SELLER` / `BUYER`) | MD=서비스 로그인 유저, SELLER=평가 대상, BUYER=주문 발생 소스. `seller_status`: `ACTIVE` / `WARNING` / `TERMINATED` |
| `courses` | 상품(product) | `instructor_id` → 셀러 ID, `enrollment_count` → 누적 판매건수, `status` → 판매중/판매중지 |
| `enrollments` | 주문(order) | `user_id` → 구매자, `course_id` → 상품, `status` → `COMPLETED` / `CANCELLED` / `RETURNED` |
| `payments` | 결제·환불 | `status` → `COMPLETED` / `REFUNDED` / `FAILED` / `CANCELLED`, `amount` → 매출액(환불 시 환불금액) |

상품 카테고리 코드: `FASHION` · `BEAUTY` · `FOOD` · `DIGITAL` · `HOME` · `SPORTS` · `BOOK` · `OTHER`

---

## 4. 아키텍처

```
                          ┌──────────────┐
   MD(부서 담당자) ──────▶ │ vue-frontend │ :3000
                          └──────┬───────┘
                                 │  (JWT)
                          ┌──────▼───────┐
                          │ API Gateway  │ :8080   토큰 검증 · 라우팅 · X-User-Id 주입
                          └──────┬───────┘
        ┌──────────────┬────────┼────────────┬──────────────┐
        ▼              ▼        ▼            ▼              ▼
 ┌────────────┐ ┌───────────┐ ┌────────────┐ ┌───────────┐ ┌────────────────────┐
 │user-service│ │course-svc │ │enrollment  │ │payment-svc│ │ recommend-service  │
 │  :8081     │ │  :8082    │ │  :8083     │ │  :8084    │ │  :8085 (FastAPI)   │
 │회원/셀러   │ │상품       │ │주문        │ │결제/환불  │ │ 셀러 평가 엔진      │
 └────────────┘ └───────────┘ └────────────┘ └─────┬─────┘ └─────────┬──────────┘
        │              │            │              │(payment.completed)│
        │              │            │◀─────────────┘ Kafka             │
        │              │            └──────────── enrollment.completed ─┘
        │              │                                                │
        └──────────────┴────────────  내부 API (평가 데이터 조회)  ◀──────┘

 인프라(수정 대상 아님, 이미지로 배포): MariaDB :3379 · Kafka :9092 · Eureka :8761 · Auth Server :9000
```

### 서비스별 역할

| 서비스 | 포트 | 역할 | 평가 엔진이 호출하는 내부 API |
| --- | --- | --- | --- |
| **user-service** | 8081 | 회원 가입·조회, 셀러 정보 관리 | `GET /api/users/internal/sellers` — 평가 대상 셀러 전체 |
| **course-service** | 8082 | 셀러 상품(가격·카테고리·판매상태) 관리 | `GET /api/courses/internal/seller/{sellerId}` — 셀러별 상품 |
| **enrollment-service** | 8083 | 주문 생성·조회, 결제 saga | `GET /api/enrollments/seller/{sellerId}` — 셀러별 주문 이력 |
| **payment-service** | 8084 | 결제·환불 처리, `payment.completed` 발행 | (Sprint 1 미사용 · Sprint 2에서 매출·환불 실측 소스) |
| **recommend-service** | 8085 | 셀러 운영 평가 엔진 (FastAPI) | `GET /api/recommend/evaluation/sellers` 제공 |
| eureka-server | 8761 | 서비스 디스커버리 | — |
| auth-server | 9000 | 로그인·JWT 발급·JWK 제공 | — |
| api-gateway | 8080 | 단일 진입점·라우팅·`X-User-Id` 주입 | — |

### 인증 / 요청 규약

- 프론트는 **API Gateway(`:8080`) 한 곳만** 호출한다. 서비스 포트를 직접 부르지 않는다.
- 프론트는 `Authorization: Bearer <accessToken>`만 실으면 되고, 게이트웨이가 JWT에서 꺼낸 `X-User-Id`를 백엔드에 주입한다.
- Java 서비스 응답은 `{ success, message, data }` 래퍼로 감싼다. **`recommend-service`는 래퍼 없이** 결과를 그대로 반환한다.

---

## 5. 셀러 평가 엔진 상세 (`recommend-service`)

### 데이터 흐름 (요청마다 즉석 계산, Kafka·DB 미사용)

```
GET /api/recommend/evaluation/sellers
  │
  ├─ ① seller_client   → user-service:  평가 대상 셀러 목록
  ├─ ② catalog_client  → course-service: 셀러별 상품(가격·카테고리)   ┐ 셀러마다 병렬 호출
  ├─ ③ order_client    → order-service:  셀러별 주문 이력(원시)        ┘
  │
  ├─ ④ aggregator      : 주문 이력 → 집계 지표(SellerMetrics)
  │                      (30일 판매량, 취소율, 환불율, 매출, 최근성 …)
  │                      COMPLETED=매출 / RETURNED=환불 / CANCELLED=취소
  │
  ├─ ⑤ evaluator       : 6개 규칙 판정 → 이슈 목록 + 종합점수 + 등급
  │
  └─ ⑥ 위험도 순 정렬   : 퇴출검토 → 주의 → 우수 → 평가보류
```

Sprint 1은 payment-service 없이 **주문 상태 × 상품 가격**으로 매출·환불을 계산한다. Sprint 2에서 payment 실제 결제 데이터로 대체한다.

### 코드 구조

```
recommend-service/
├── main.py                       FastAPI 앱, Eureka 등록, Kafka consumer 기동
├── requirements.txt
├── Dockerfile
├── pytest.ini
├── app/
│   ├── config/
│   │   ├── settings.py            환경변수 (서비스 URL 등)
│   │   └── security.py            JWT 검증 (JWK from auth-server)
│   ├── client/
│   │   ├── seller_client.py       user-service 호출
│   │   ├── catalog_client.py      course-service 호출
│   │   └── order_client.py        order-service 호출
│   ├── rules/
│   │   ├── thresholds.py          임계값·가중치·카테고리 기준액 (상수만)
│   │   ├── aggregator.py          원시 주문 → 집계 지표 (순수 함수)
│   │   └── evaluator.py           6개 규칙 + 종합점수·등급 (순수 함수)
│   ├── service/
│   │   └── evaluation_service.py  ①~⑥ 오케스트레이션
│   ├── router/
│   │   └── evaluation_router.py   GET /api/recommend/evaluation/sellers
│   ├── model/
│   │   └── schemas.py             Pydantic 모델 (내부 지표 · 응답 계약)
│   └── kafka/
│       └── consumer.py            Sprint 1 미사용 (원본 유지, Sprint 2용)
└── tests/
    └── test_evaluator.py          6개 규칙 경계값 + 집계 + 점수/등급 (40 케이스)
```

> 엔드포인트 prefix가 `/api/recommend/evaluation`인 이유: api-gateway(소스 없음)가 `/api/recommend/**`만 이 서비스로 라우팅하므로 그 아래에 붙였다.

### 테스트

```bash
cd recommend-service
python -m pytest -q          # 40 케이스
```

---

## 6. 전체 코드 구조

```
skala-msa-lecture/
├── docker-compose.yml            운영(이미지) 구성 — 기본
├── docker-compose.override.yml   로컬 소스 반영용 (자동 병합)
├── docker-compose.build.yml      전체 소스 재빌드 구성
├── scripts/build-local.sh        네트워크 없이 Java 패치 jar 생성
├── init-db/
│   ├── 01_init.sql               스키마 (users·courses·enrollments·payments)
│   └── 02_seed.sql               데모 시드 (MD 1 · 구매자 10 · 셀러 12 · 60일 주문/결제)
├── docs/
│   ├── API_SPEC.md               (초기 피벗 버전 — 최신 아님, 참고만)
│   └── FE_BE_HANDOFF.md
│
├── user-service/         (Java · Spring Boot)   회원/셀러
│   └── src/main/java/com/lecture/user/
│       ├── controller/UserController.java
│       ├── service/UserService.java
│       ├── entity/User.java          Role(MD/SELLER/BUYER), SellerStatus
│       ├── dto/UserDto.java
│       └── repository/UserRepository.java
│
├── course-service/       (Java · Spring Boot)   상품
│   └── src/main/java/com/lecture/course/
│       ├── controller/CourseController.java   /internal/seller/{sellerId} 추가
│       ├── service/CourseService.java
│       ├── entity/Course.java
│       └── ...
│
├── enrollment-service/   (Java · Spring Boot)   주문 + 결제 saga
│   └── src/main/java/com/lecture/enrollment/
│       ├── controller/EnrollmentController.java  /seller/{sellerId} 추가
│       ├── service/EnrollmentService.java, EnrollmentWriteService.java
│       ├── service/CourseServiceClient.java, PaymentServiceClient.java
│       ├── entity/Enrollment.java     Status(COMPLETED/CANCELLED/RETURNED)
│       └── kafka/                     Producer / Consumer / KafkaEvent
│
├── payment-service/      (Java · Spring Boot)   결제·환불
│   └── src/main/java/com/lecture/payment/
│       ├── controller/PaymentController.java
│       ├── service/PaymentService.java
│       ├── entity/Payment.java
│       └── kafka/PaymentKafkaProducer.java     payment.completed
│
├── recommend-service/    (Python · FastAPI)     셀러 평가 엔진  ← 5장 참고
│
├── vue-frontend/         (Vue 3 · Vite)         MD 대시보드
│   └── src/
│       ├── api/            index.js · auth.js · product.js · evaluation.js
│       ├── store/          auth.js · product.js · evaluation.js (Pinia)
│       ├── router/index.js
│       ├── constants/evaluation.js   등급/이슈 라벨·색상 매핑
│       ├── components/md/  GradeBadge · IssueTag · MdSidebar
│       └── views/md/       SellerRankingView · SellerDetailView ·
│                           MdDashboardView · ProductListView · MdWatchlistView
│
└── eureka-server/        (Java)   서비스 디스커버리 (소스 이해용, 수정 X)
     # auth-server / api-gateway 는 이미지로만 배포 (소스 없음)
```

---

## 7. 실행 방법

### 사전 준비 — 이미지 로드 (최초 1회)

```bash
# 인프라 이미지 (auth-server, api-gateway, kafka)
docker load -i infra-images.tar

# 마이크로서비스 이미지 (분할 파일 합치기)
cat msa-lecture-images.part* > msa-lecture-images.tar.gz
docker load -i msa-lecture-images.tar.gz

docker images     # msa-lecture/auth-server:1.0, msa-lecture-*:latest 확인
```

### A. 로컬 소스 반영 실행 (권장 · 네트워크 불필요)

`docker-compose.override.yml`이 자동 병합되어, 패치한 Java jar와 recommend-service 소스를 컨테이너에 마운트한다.

```bash
# 1) Java 서비스(user/course/enrollment)를 로컬 소스로 재컴파일 → 패치 jar 생성
./scripts/build-local.sh

# 2) 기동 (override 가 패치 jar / recommend 소스를 마운트)
docker compose up -d

# 이후 소스만 고쳤을 때
./scripts/build-local.sh course-service
docker compose restart course-service recommend-service
```

### B. 전체 재빌드 (Gradle/네트워크 필요)

```bash
docker compose -f docker-compose.build.yml build --no-cache
docker compose -f docker-compose.build.yml up -d
```

### 기동 순서 (depends_on)

```
MariaDB / Kafka  →  Eureka  →  Auth Server  →  API Gateway + 4개 서비스  →  Recommend Service
```

### 확인

| 대상 | URL |
| --- | --- |
| Eureka 대시보드 | http://localhost:8761 |
| API Gateway | http://localhost:8080 |
| user / course / enrollment / payment Swagger | http://localhost:8081~8084/swagger-ui/index.html |
| recommend-service docs | http://localhost:8085/docs |
| 프론트엔드 | http://localhost:3000 |

### 로그

```bash
docker compose logs -f                       # 전체
docker compose logs -f recommend-service      # 개별
```

### 종료

```bash
docker compose down            # 컨테이너 정리
docker compose down -v         # DB 볼륨까지 삭제 (init-db 재실행하려면 필수)
```

> **스키마·시드를 바꿨으면** `docker compose down -v` 후 다시 올려야 `init-db`가 재실행된다.

### 프론트엔드 (로컬 개발)

```bash
cd vue-frontend
npm install
npm run dev        # http://localhost:3000
```

### 데모 계정

`init-db/02_seed.sql` 기준. 비밀번호는 전부 `password123`.

| 역할 | 계정 |
| --- | --- |
| MD (로그인 유저) | `md@example.com` |
| 셀러 (평가 대상) | `seller01@example.com` ~ `seller12@example.com` |
| 구매자 (데이터 소스) | `buyer01@example.com` ~ `buyer10@example.com` |

셀러 12명은 우수 4 · 주의 4 · 퇴출검토 4로 나뉘어 6개 규칙이 실제 트리거되도록 최근 60일 주문·결제가 시드되어 있다.

---

## 8. 스프린트 구분

### Sprint 1 (완료) — 워킹 스켈레톤

| 기능 | 서비스 |
| --- | --- |
| 도메인 재해석 + 시드 데이터 (셀러·상품·주문·결제) | `init-db` |
| 평가 대상 셀러 / 셀러별 상품 / 셀러별 주문 조회 내부 API | `user·course·enrollment-service` |
| 6개 규칙 기반 셀러 랭킹·등급 산출 | `recommend-service` |
| 로그인 → 셀러 평가 랭킹 → 등급·이슈·근거 확인 | `vue-frontend` |

동기 REST만 사용. payment·Kafka는 원본 그대로 통과.

### Sprint 2 (예정) — 확장

| 기능 | 서비스 |
| --- | --- |
| 관심 셀러 등록/해제 (평가 대상을 전체 → 관심 셀러로 축소) | `order-service`, `init-db` |
| 결제·환불 이벤트 발행 (토픽·구조 유지, payload 확장) | `payment-service` |
| `payment.completed` 수신 → 주문 상태 자동 전환 | `order-service` |
| 이벤트 기반 평가 갱신 (해당 셀러만 재계산·캐시) | `recommend-service` |
| 매출·환불을 주문 상태 추정 → **payment 실제 결제 데이터로 대체** | `recommend-service` |
| 보류(None) 규칙 N개↑ → 등급 하향 (데이터 부족 셀러 보정) | `recommend-service` |
| 셀러 단건 상세 API `GET /api/recommend/evaluation/sellers/{id}` | `recommend-service` |
| 관심 셀러 관리 화면, 등급 변화 추이, 이슈 처리 상태 | `vue-frontend` |

### Sprint 3 (구상) — 규칙 → ML

조건 규칙을 이상탐지(Isolation Forest) → 로지스틱 회귀(임계값 학습) → LightGBM+SHAP(위험 예측+근거)로 단계 교체. 규칙 버전은 baseline으로 유지하고 Precision@K로 비교.

---

## 9. 팀 구성

| 이름 | 역할 | 담당 |
| --- | --- | --- |
| 정서현 / 채석현 | PM | 프로젝트 기획, 성능·우선순위 정의, 발표 |
| 권하림 / 최윤경 | Frontend | 대시보드 UI, API 연동 |
| 정선웅 | Backend | 회원·상품·주문·결제 서비스 + `init-db`, 평가용 내부 API |
| 표성주 | Backend | 셀러 평가 엔진(`recommend-service`) — 규칙·집계·점수/등급 |
