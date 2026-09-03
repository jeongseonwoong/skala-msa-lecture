# 프론트 ↔ 백엔드 협업 정리

> Sprint 1 착수 시점 공유 문서. **API 상세는 [API_SPEC.md](./API_SPEC.md)** 참고.
> 최종 수정: 2026-09-03 · 상태: **설계 확정 대기** (백엔드 코드 미변경)

---

## 1. 한 줄 요약

기존 **온라인 강의 플랫폼** 템플릿을 **이커머스 상품 이슈 모니터링 솔루션**으로 전환합니다.
셀러가 매일 아침 여러 채널 데이터를 엑셀로 취합하던 1~2시간을 없애는 것이 목표입니다.

**핵심 사용자 여정 (Sprint 1 데모)**

```
로그인 → 상품 등록 → 모니터링 지정 → 아침 CSV 업로드 → "오늘 볼 상품 12개" 우선순위 리스트 → 상품 클릭 → 이슈 상세
```

---

## 2. 용어 대조표 — 같은 테이블, 다른 의미

**중요:** 테이블·클래스·URL 경로는 **기존 이름을 그대로 씁니다.** 의미만 바뀝니다.
코드에서 `course`를 보면 "상품", `enrollment`을 보면 "모니터링 대상"으로 읽으세요.

| 기존 도메인 | 새 도메인 | 유지되는 식별자 |
| --- | --- | --- |
| 강의 (Course) | **상품** (ProductCatalog) | 테이블 `courses`, 클래스 `Course`, 경로 `/api/courses` |
| 수강신청 (Enrollment) | **모니터링 대상** (WatchItem) | 테이블 `enrollments`, 클래스 `Enrollment`, 경로 `/api/enrollments` |
| 강사 (instructor) | **셀러 / 운영자** (seller) | 필드는 `sellerId`로 **변경됨** |
| 수강생 수 | **모니터링 지정 수** | 필드는 `watchCount`로 **변경됨** |
| 강의 추천 | **이슈 상품 랭킹 · 권장 액션** | 서비스 `recommend-service` |
| — | **일일 운영 지표** (ProductMetric) | 신규 테이블 `product_metrics` |

> 왜 이름을 안 바꾸나: 게이트웨이 라우팅·Eureka 등록명·Kafka 토픽·docker-compose 서비스명이 전부 얽혀 있어
> 리네이밍 비용 대비 얻는 게 없습니다. **DTO 필드명만** 도메인에 맞게 바꿉니다.

---

## 3. Sprint 1 범위

### 포함

| 서비스 | 하는 일 |
| --- | --- |
| `init-db` | `courses`에 `sku`·`list_price`·`cost`·`season`·`season_end_date`·`target_margin_rate` 추가, `enrollments`에 `monitor_status`·`issue_summary`·`priority_score` 추가, `product_metrics` 신규 테이블, 시드 데이터(상품 50개 + 30~60일 이력) |
| `course-service` | 상품 등록 / 목록 / 상세 / 카테고리별 |
| `enrollment-service` | 모니터링 지정, 내 모니터링 목록, **CSV 업로드 → 지표 저장** |
| `recommend-service` | 조건 규칙 8종 **즉석 계산** → 이슈 태깅·심각도·우선순위·권장 액션 |
| `vue-frontend` | 위 여정 5화면 |

### 제외 (Sprint 2)

- 구독 결제 (`payment-service`) — **Sprint 1에서 결제 호출 자체를 제거**
- Kafka 비동기 (`payment.completed` → 분석 활성화)
- 이슈 처리 상태 변경 (확인 / 조치중 / 해결)
- 이슈 리포트 선계산·저장, 이슈 이력
- 상품 수정·삭제, 모니터링 해제, 페이징·검색

---

## 4. 프론트가 지금 당장 알아야 할 것 (Breaking Changes)

### 🔴 반드시 고쳐야 하는 것

| # | 내용 | 조치 |
| --- | --- | --- |
| 1 | `recommend-service`만 **응답 래퍼가 없음** (FastAPI) | `res.data.data` → `res.data` |
| 2 | 카테고리가 **영문 코드**로 옴 (서버 한글 변환 제거) | 프론트에 라벨 매핑 테이블 추가 |
| 3 | `instructorId` → `sellerId` | `MyPageView.vue` |
| 4 | `enrollmentCount` → `watchCount` | `CourseCard.vue`, `CourseDetailView.vue`, `MyPageView.vue` |
| 5 | `enrollment.status` → `monitorStatus`, `PENDING` 값 사라짐 | 상태 뱃지 매핑 |
| 6 | `enrollment.course` → `enrollment.product` | `MyPageView.vue` |
| 7 | `GET /api/recommend/{userId}` → `/api/recommend/issues/{userId}` | `api/enrollment.js` |

### 🟡 호출하면 404 (Sprint 1 미구현)

- `api/enrollment.js` 의 `cancel(enrollmentId)` → `DELETE /api/enrollments/{id}`
- `api/course.js` 의 `update(id, data)` → `PUT /api/courses/{id}`
- `GET /api/courses` 의 `params` — 서버가 무시함 (페이징·검색 없음)

### 🟢 그대로 두면 되는 것

- 인증 흐름 전체 (`/oauth2/token`, `/api/users/me`, `/api/users/register`)
- `src/api/index.js` axios 인터셉터 — `Authorization` 헤더 자동 부착
- 게이트웨이 단일 진입점 `:8080`
- `POST /api/enrollments` 요청 바디 `{ courseId }`

---

## 5. 화면 ↔ API 매핑

| 화면 | 호출 | 비고 |
| --- | --- | --- |
| 로그인 | `POST /oauth2/token` → `GET /api/users/me` | `me.id`를 이슈 조회의 `{userId}`로 보관 |
| 상품 등록 | `POST /api/courses` | `sku`는 CSV 매칭 키 — 입력 가이드 문구 필요 |
| 상품 목록 | `GET /api/courses` | 카드에서 "모니터링 추가" 버튼 |
| 모니터링 지정 | `POST /api/enrollments` `{courseId}` | 중복 시 400 → 토스트 |
| 내 모니터링 | `GET /api/enrollments/my` | `product` 동봉 — 상품 상세 추가 호출 불필요 |
| **CSV 업로드** | `POST /api/enrollments/metrics/upload` | `FormData`, 파트명 `file`, 템플릿 다운로드 버튼 권장 |
| **오늘 볼 상품** | `GET /api/recommend/issues/{userId}` | 정렬은 서버가 완료. `grade`로 뱃지 색 분기 |
| 이슈 상세 | 위 응답의 `items[].issues[]` | 추가 호출 없음 — `evidence` 문장 그대로 출력 |

**화면 카피 힌트**
- 헤더: `"{totalWatched}개 중 {items.length}개 상품에 이슈"`
- 기준일: `"{metricDate} 데이터 기준"` — 오늘 업로드 안 했으면 과거 날짜가 오므로 반드시 노출
- 업로드 결과: `"48건 반영 · 2건 건너뜀"` + 상세는 접기

---

## 6. 서비스 간 의존 (Sprint 1)

```
vue-frontend
    │  (Bearer token)
    ▼
api-gateway :8080  ──── X-User-Id 주입 ────┐
    │                                       │
    ├──► course-service :8082  (상품 카탈로그)
    │         ▲                    ▲
    │         │ internal REST      │ internal REST
    ├──► enrollment-service :8083 ─┘        │
    │         ▲   (모니터링 + product_metrics)
    │         │ internal REST                │
    └──► recommend-service :8085 ────────────┘
              (조건 규칙 즉석 계산 · 저장 없음)
```

**내부 REST (프론트 미사용, 백엔드끼리만)**

| 호출자 | 대상 | 용도 |
| --- | --- | --- |
| enrollment | `GET /api/courses/internal/exists/{id}` | 상품 존재 확인 |
| enrollment | `GET /api/courses/internal/{id}` | 목록 조립용 상품 상세 |
| enrollment | `GET /api/courses/internal/attrs?ids=` | **신규** — 벌크 속성 조회 |
| recommend | `GET /api/enrollments/internal/monitoring/{userId}` | **신규** — 모니터링 상품 + 최신 지표 |
| recommend | `GET /api/courses/internal/attrs?ids=` | 원가·목표마진·시즌 등 규칙 입력값 |

> Sprint 1에서 Kafka는 쓰지 않습니다. 코드는 남겨두되 발행 경로를 타지 않습니다.

---

## 7. 아직 정해지지 않은 것 — 확정 필요

| # | 항목 | 선택지 | 기본안 |
| --- | --- | --- | --- |
| 1 | 필드 리네이밍 범위 | ⓐ `sellerId`/`watchCount`/`monitorStatus`까지 전부 변경 ⓑ 이름 유지, 의미만 전환 | **ⓐ** — 도메인 가독성. 프론트 7곳 수정 발생 |
| 2 | CSV 매칭 키 | ⓐ `sku` ⓑ 상품 PK `id` | **ⓐ** — 셀러가 실제 쓰는 코드. 단 `courses.sku` 컬럼 신설 필요 |
| 3 | 카테고리 평균 반품률 | ⓐ 상수 테이블 하드코딩 ⓑ 업로드 데이터에서 실시간 산출 | **ⓐ** — Sprint 1은 상수, Sprint 2에서 산출 |
| 4 | `targetMarginRate` 위치 | ⓐ 상품별 속성 ⓑ 전역 설정값 | **ⓐ** — 카테고리별 마진이 크게 다름 |
| 5 | 결제 호출 제거 | 현재 `enroll()`이 99,000원 결제를 요청 중 | **제거** — 클래스는 남기고 호출만 삭제 |
| 6 | 시드 데이터 규모 | 상품 50개 / 이력 30~60일 | 데모 화면에 이슈가 10~15개 뜨도록 튜닝 |

---

## 8. 작업 순서 & 체크리스트

권장 순서 — **DDL → 백엔드 → 프론트**. 백엔드 API가 뜨기 전 프론트는 목 데이터로 진행 가능.

### 백엔드

- [ ] `init-db/01_init.sql` — 컬럼 추가 + `product_metrics` 테이블 + 시드
- [ ] `course-service` — Entity → DTO → Repository → Service → Controller
- [ ] `enrollment-service` — `Enrollment` 수정 + `ProductMetric` 신규 + CSV 파싱 서비스
- [ ] `enrollment-service` — 결제 호출 제거, internal 모니터링 스냅샷 API
- [ ] `recommend-service` — 규칙 8종 계산, `/api/recommend/issues/{userId}`
- [ ] 게이트웨이 라우팅 확인 (경로 유지이므로 변경 불필요할 것으로 예상)

### 프론트

- [ ] Enum 라벨 매핑 유틸 (`Category`, `Season`, `MonitorStatus`, `IssueType`, `Action`)
- [ ] `api/course.js` — 등록 폼 필드 확장, `update` 제거
- [ ] `api/enrollment.js` — `uploadMetrics()` 추가, `getRecommendations()` 경로 변경, `cancel` 제거
- [ ] `CourseCard.vue` / `CourseDetailView.vue` / `MyPageView.vue` — 필드명 6곳 교체
- [ ] 상품 등록 폼 (`sku`·`listPrice`·`cost`·`season`·`seasonEndDate`·`targetMarginRate`)
- [ ] CSV 업로드 화면 + 템플릿 다운로드 + 결과 요약
- [ ] **"오늘 볼 상품" 리스트** — `grade`별 뱃지, 대표 이슈 + `+N`, `evidence` 출력
- [ ] 이슈 상세 패널

---

## 9. 로컬 실행

```bash
# 백엔드 전체 (프로젝트 루트)
docker load -i infra-images.tar
docker compose build --no-cache && docker compose up -d

# 기동 확인 — Eureka에 서비스 등록 상태
open http://localhost:8761/

# 프론트
cd vue-frontend && npm install && npm run dev
open http://localhost:3000
```

| 컴포넌트 | 포트 |
| --- | --- |
| api-gateway | `8080` ← **프론트는 여기만** |
| auth-server | `9000` |
| eureka | `8761` |
| user / course / enrollment / payment / recommend | `8081` / `8082` / `8083` / `8084` / `8085` |
| MariaDB | `3379` (컨테이너 내부 3306) |
| Kafka | `9092` |

`docker compose logs -f course-service` 로 개별 로그 확인.

---

## 10. 연락 · 변경 관리

- API 변경이 생기면 **[API_SPEC.md](./API_SPEC.md)를 먼저 고치고** 공유합니다. 구두 합의만으로 필드를 바꾸지 않습니다.
- 프론트가 목 데이터를 만들 때는 API_SPEC의 JSON 예시를 그대로 복사해 쓰면 필드 누락이 없습니다.
- Sprint 1 데모 기준 통과 조건: **CSV 업로드 한 번으로 "오늘 볼 상품" 리스트가 이슈 태그·근거·권장 액션과 함께 우선순위로 표시될 것.**
