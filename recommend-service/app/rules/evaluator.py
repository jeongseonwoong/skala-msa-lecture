"""셀러 운영 평가 규칙 엔진.

각 규칙은 순수 함수다:
    (셀러 지표 dict) -> {type, severity(0~1), evidence(str)}  또는  None

- 외부 I/O·상태 없음 → 유닛 테스트로 단독 검증 가능(tests/test_evaluator.py)
- 지표가 없거나 비교 기준(분모)이 0이면 해당 규칙은 None(판정 보류)
- severity 는 "임계값을 얼마나 초과/미달했는지"를 0~1 로 정규화한 값

지표 dict 키(snake_case)는 app.model.schemas.SellerMetrics 와 동일하다.
order-service 의 실제 필드명 매핑은 app/client/order_client.py 한 곳에서만 처리한다.
"""

from __future__ import annotations

from typing import Callable, Optional

from app.rules import thresholds as T

Metrics = dict
Issue = dict


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _num(m: Metrics, key: str, default: float = 0.0) -> float:
    value = m.get(key, default)
    return default if value is None else float(value)


def compute_category_avg_sales_30d(sellers: list[Metrics]) -> dict[str, float]:
    """관심 셀러 목록에서 카테고리별 30일 평균 판매량을 계산.

    LOW_SALES 규칙의 비교 기준값. order-service 가 주지 않고 이 서비스가
    "지금 평가 대상인 관심 셀러들" 안에서 카테고리별 단순 평균을 낸다(본인 포함).

    주의: 한 카테고리에 셀러가 1명뿐이면 평균 = 본인 값 → 비율 1.0 → 사실상
    LOW_SALES 가 발동하지 않는다(비교 대상이 없으므로 정상 동작).
    """
    buckets: dict[str, list[float]] = {}
    for m in sellers:
        category = str(m.get("category") or "").upper()
        if not category:
            continue
        buckets.setdefault(category, []).append(_num(m, "sales_count_30d"))
    return {cat: sum(values) / len(values) for cat, values in buckets.items() if values}


# ---------------------------------------------------------------------------
# 개별 규칙 (6개)
# ---------------------------------------------------------------------------

def check_low_sales(m: Metrics) -> Optional[Issue]:
    """최근 30일 판매량이 카테고리 평균의 LOW_SALES_RATIO 미만."""
    sales = _num(m, "sales_count_30d")
    category_avg = _num(m, "category_avg_sales_30d")
    if category_avg <= 0:
        return None

    ratio = sales / category_avg
    if ratio >= T.LOW_SALES_RATIO:
        return None

    severity = _clamp((T.LOW_SALES_RATIO - ratio) / T.LOW_SALES_RATIO)
    return {
        "type": "LOW_SALES",
        "severity": severity,
        "evidence": (
            f"최근 30일 판매량이 카테고리 평균의 {ratio * 100:.0f}% "
            f"(기준 {T.LOW_SALES_RATIO * 100:.0f}% 미만)"
        ),
    }


def check_sales_declining(m: Metrics) -> Optional[Issue]:
    """최근 7일 판매량이 이전 7일의 SALES_DECLINING_RATIO 미만."""
    recent = _num(m, "sales_7d")
    prev = _num(m, "sales_prev_7d")
    if prev <= 0:
        return None

    ratio = recent / prev
    if ratio >= T.SALES_DECLINING_RATIO:
        return None

    severity = _clamp((T.SALES_DECLINING_RATIO - ratio) / T.SALES_DECLINING_RATIO)
    return {
        "type": "SALES_DECLINING",
        "severity": severity,
        "evidence": (
            f"최근 7일 판매량이 이전 7일의 {ratio * 100:.0f}% "
            f"(기준 {T.SALES_DECLINING_RATIO * 100:.0f}% 미만)"
        ),
    }


def check_high_cancel_rate(m: Metrics) -> Optional[Issue]:
    """(취소 + 반품) ÷ 전체 주문 > HIGH_CANCEL_RATE."""
    total = _num(m, "total_order_count")
    bad = _num(m, "cancel_return_count")
    if total <= 0:
        return None

    rate = bad / total
    if rate <= T.HIGH_CANCEL_RATE:
        return None

    severity = _clamp((rate - T.HIGH_CANCEL_RATE) / (1.0 - T.HIGH_CANCEL_RATE))
    return {
        "type": "HIGH_CANCEL_RATE",
        "severity": severity,
        "evidence": (
            f"취소·반품률 {rate * 100:.0f}% "
            f"(기준 {T.HIGH_CANCEL_RATE * 100:.0f}% 초과)"
        ),
    }


def check_high_refund_rate(m: Metrics) -> Optional[Issue]:
    """환불 금액 ÷ 총 결제 금액 > HIGH_REFUND_RATE."""
    paid = _num(m, "total_payment_amount")
    refund = _num(m, "refund_amount")
    if paid <= 0:
        return None

    rate = refund / paid
    if rate <= T.HIGH_REFUND_RATE:
        return None

    severity = _clamp((rate - T.HIGH_REFUND_RATE) / (1.0 - T.HIGH_REFUND_RATE))
    return {
        "type": "HIGH_REFUND_RATE",
        "severity": severity,
        "evidence": (
            f"환불율 {rate * 100:.0f}% "
            f"(기준 {T.HIGH_REFUND_RATE * 100:.0f}% 초과)"
        ),
    }


def check_low_revenue(m: Metrics) -> Optional[Issue]:
    """최근 30일 매출이 카테고리별 최소 유지 기준액 미달."""
    revenue = _num(m, "revenue_30d")
    category = str(m.get("category") or "").upper()
    min_required = T.CATEGORY_MIN_REVENUE_30D.get(
        category, T.CATEGORY_MIN_REVENUE_DEFAULT
    )

    if revenue >= min_required:
        return None

    severity = _clamp((min_required - revenue) / min_required)
    return {
        "type": "LOW_REVENUE",
        "severity": severity,
        "evidence": (
            f"최근 30일 매출 {revenue:,.0f}원 "
            f"(카테고리 최소 기준 {min_required:,.0f}원 미달)"
        ),
    }


def check_no_recent_order(m: Metrics) -> Optional[Issue]:
    """최근 NO_RECENT_ORDER_DAYS(14)일간 신규 주문 0건.

    우선순위: new_orders_14d(정확) → days_since_last_order(대체).
    둘 다 없으면 판정 보류(None).
    """
    new_orders_14d = m.get("new_orders_14d")
    days_since = m.get("days_since_last_order")

    if new_orders_14d is not None:
        triggered = float(new_orders_14d) == 0
    elif days_since is not None:
        triggered = float(days_since) >= T.NO_RECENT_ORDER_DAYS
    else:
        return None

    if not triggered:
        return None

    if days_since is not None:
        detail = f"최근 주문일로부터 {int(days_since)}일 경과"
    else:
        detail = f"최근 {T.NO_RECENT_ORDER_DAYS}일간 신규 주문 없음"

    # 신규 주문 0건은 이분법적 이슈 → 심각도 최대
    return {
        "type": "NO_RECENT_ORDER",
        "severity": 1.0,
        "evidence": f"신규 주문 없음 ({detail})",
    }


# 규칙 실행 순서(응답 issues 배열 순서와 동일)
RULES: list[Callable[[Metrics], Optional[Issue]]] = [
    check_low_sales,
    check_sales_declining,
    check_high_cancel_rate,
    check_high_refund_rate,
    check_low_revenue,
    check_no_recent_order,
]


# ---------------------------------------------------------------------------
# 종합 판정
# ---------------------------------------------------------------------------

def _grade(score: int) -> str:
    if score >= T.GRADE_EXCELLENT_MIN:
        return T.GRADE_EXCELLENT
    if score >= T.GRADE_WARNING_MIN:
        return T.GRADE_WARNING
    return T.GRADE_AT_RISK


def evaluate_seller(metrics: Metrics) -> dict:
    """셀러 1명의 지표 dict → 이슈 목록 + 종합점수 + 등급.

    반환:
        {
          "issues":  [{type, severity, evidence}, ...],
          "penalty": float,   # Σ(severity × weight) — 위험도 정렬 키
          "score":   int,     # 0~100, 높을수록 우량
          "grade":   str,     # 우수 / 주의 / 퇴출검토
        }
    """
    issues: list[Issue] = []
    for rule in RULES:
        result = rule(metrics)
        if result is not None:
            issues.append(result)

    penalty = sum(
        issue["severity"] * T.ISSUE_WEIGHTS[issue["type"]] for issue in issues
    )
    score = int(round(_clamp(T.BASE_SCORE - penalty, 0, 100)))

    return {
        "issues": issues,
        "penalty": penalty,
        "score": score,
        "grade": _grade(score),
    }
