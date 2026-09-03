"""셀러 운영 평가 엔진 - 규칙 임계값 / 가중치 상수.

이 값들은 Sprint 3에서 데이터 기반으로 튜닝될 예정이므로 규칙 로직과 분리한다.
(evaluator.py 는 이 모듈의 상수만 참조하고, 매직넘버를 직접 갖지 않는다.)
"""

# ---------------------------------------------------------------------------
# 1) 이슈 판정 임계값
# ---------------------------------------------------------------------------

# LOW_SALES: 최근 30일 판매량 ÷ 카테고리 평균 판매량 < 0.5
LOW_SALES_RATIO = 0.5

# SALES_DECLINING: 최근 7일 판매량 ÷ 이전 7일 판매량 < 0.7
SALES_DECLINING_RATIO = 0.7

# HIGH_CANCEL_RATE: (취소 + 반품 건수) ÷ 전체 주문 건수 > 0.15
HIGH_CANCEL_RATE = 0.15

# HIGH_REFUND_RATE: 환불 금액 ÷ 총 결제 금액 > 0.10
HIGH_REFUND_RATE = 0.10

# NO_RECENT_ORDER: 최근 14일 신규 주문 0건
NO_RECENT_ORDER_DAYS = 14

# LOW_REVENUE: 최근 30일 매출 < 카테고리별 최소 유지 기준액(원)
#   - 데이터가 아니라 비즈니스 설정값이므로 여기에 상수로 둔다(백엔드 협의 불필요).
#   - 카테고리 문자열은 order-service 가 내려주는 category 값과 대문자로 맞춘다.
CATEGORY_MIN_REVENUE_30D = {
    "FASHION": 3_000_000,
    "BEAUTY": 2_000_000,
    "FOOD": 2_500_000,
    "LIVING": 2_000_000,
    "DIGITAL": 5_000_000,
    "ETC": 1_000_000,
}
CATEGORY_MIN_REVENUE_DEFAULT = 1_000_000


# ---------------------------------------------------------------------------
# 2) 종합점수 / 등급
# ---------------------------------------------------------------------------
# 종합점수 = BASE_SCORE - Σ(이슈 심각도 × 가중치), 0~100 으로 clamp.
#
#   ※ 지침 문구는 "종합점수 = Σ(이슈 심각도 × 가중치)" 였으나, 지침의 응답 예시
#     (score 38 → "퇴출검토")와 등급 기준("80 이상 우수 / 50 미만 퇴출검토")은
#     "점수가 높을수록 우량 셀러"를 전제한다. 두 조건을 모두 만족시키려면
#     Σ(심각도×가중치)는 '감점(penalty)'으로 쓰고 100에서 빼야 한다.
#     → penalty 자체는 evaluate_seller() 결과에 함께 담아 정렬 키로 사용한다.
BASE_SCORE = 100

# 가중치 합 = 100  → 모든 이슈가 심각도 1.0 이면 점수 0점
ISSUE_WEIGHTS = {
    "HIGH_CANCEL_RATE": 25,
    "HIGH_REFUND_RATE": 20,
    "LOW_SALES": 15,
    "SALES_DECLINING": 15,
    "LOW_REVENUE": 15,
    "NO_RECENT_ORDER": 10,
}

# 등급 경계 (종합점수 기준)
GRADE_EXCELLENT_MIN = 80   # score >= 80        → 우수
GRADE_WARNING_MIN = 50     # 50 <= score < 80   → 주의
#                            score < 50         → 퇴출검토

GRADE_EXCELLENT = "우수"
GRADE_WARNING = "주의"
GRADE_AT_RISK = "퇴출검토"
