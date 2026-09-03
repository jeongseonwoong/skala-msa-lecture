"""6개 규칙 함수 + 종합 판정 유닛 테스트.

각 규칙에 대해 경계값(정확히 임계값 / 임계값 직전 / 임계값 직후)을 검증한다.
외부 I/O 없음 → `pytest` 만으로 실행.
"""

import pytest

from app.rules import thresholds as T
from app.rules.evaluator import (
    check_high_cancel_rate,
    check_high_refund_rate,
    check_low_revenue,
    check_low_sales,
    check_no_recent_order,
    check_sales_declining,
    compute_category_avg_sales_30d,
    evaluate_seller,
)


# ---------------------------------------------------------------------------
# 헬퍼: 이슈가 하나도 안 잡히는 "정상 셀러" 기준 지표
# ---------------------------------------------------------------------------
def healthy_metrics(**overrides) -> dict:
    m = {
        "seller_id": 1,
        "seller_name": "정상상회",
        "category": "FASHION",
        "sales_count_30d": 500.0,        # 카테고리 평균과 동일
        "category_avg_sales_30d": 500.0,
        "sales_7d": 100.0,               # 이전 7일과 동일
        "sales_prev_7d": 100.0,
        "cancel_return_count": 5,        # 5%
        "total_order_count": 100,
        "refund_amount": 10_000.0,       # 1%
        "total_payment_amount": 1_000_000.0,
        "revenue_30d": 10_000_000.0,     # FASHION 기준(3M) 훨씬 초과
        "days_since_last_order": 1,
        "new_orders_14d": 20,
    }
    m.update(overrides)
    return m


# ---------------------------------------------------------------------------
# LOW_SALES : 30일 판매량 / 카테고리 평균 < 0.5
# ---------------------------------------------------------------------------
class TestLowSales:
    def test_exactly_at_threshold_is_not_issue(self):
        m = healthy_metrics(sales_count_30d=50.0, category_avg_sales_30d=100.0)  # ratio 0.5
        assert check_low_sales(m) is None

    def test_just_below_threshold_is_issue(self):
        m = healthy_metrics(sales_count_30d=49.0, category_avg_sales_30d=100.0)  # ratio 0.49
        issue = check_low_sales(m)
        assert issue is not None
        assert issue["type"] == "LOW_SALES"
        assert 0.0 < issue["severity"] <= 1.0

    def test_just_above_threshold_is_not_issue(self):
        m = healthy_metrics(sales_count_30d=51.0, category_avg_sales_30d=100.0)  # ratio 0.51
        assert check_low_sales(m) is None

    def test_zero_category_average_holds_judgement(self):
        m = healthy_metrics(sales_count_30d=0.0, category_avg_sales_30d=0.0)
        assert check_low_sales(m) is None

    def test_zero_sales_gives_max_severity(self):
        m = healthy_metrics(sales_count_30d=0.0, category_avg_sales_30d=100.0)
        assert check_low_sales(m)["severity"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# SALES_DECLINING : 최근 7일 / 이전 7일 < 0.7
# ---------------------------------------------------------------------------
class TestSalesDeclining:
    def test_exactly_at_threshold_is_not_issue(self):
        m = healthy_metrics(sales_7d=70.0, sales_prev_7d=100.0)  # ratio 0.7
        assert check_sales_declining(m) is None

    def test_just_below_threshold_is_issue(self):
        m = healthy_metrics(sales_7d=69.0, sales_prev_7d=100.0)
        assert check_sales_declining(m)["type"] == "SALES_DECLINING"

    def test_just_above_threshold_is_not_issue(self):
        m = healthy_metrics(sales_7d=71.0, sales_prev_7d=100.0)
        assert check_sales_declining(m) is None

    def test_zero_previous_week_holds_judgement(self):
        m = healthy_metrics(sales_7d=0.0, sales_prev_7d=0.0)
        assert check_sales_declining(m) is None


# ---------------------------------------------------------------------------
# HIGH_CANCEL_RATE : (취소+반품) / 전체 주문 > 0.15
# ---------------------------------------------------------------------------
class TestHighCancelRate:
    def test_exactly_at_threshold_is_not_issue(self):
        m = healthy_metrics(cancel_return_count=15, total_order_count=100)  # 0.15
        assert check_high_cancel_rate(m) is None

    def test_just_above_threshold_is_issue(self):
        m = healthy_metrics(cancel_return_count=16, total_order_count=100)  # 0.16
        issue = check_high_cancel_rate(m)
        assert issue["type"] == "HIGH_CANCEL_RATE"
        assert "16%" in issue["evidence"]

    def test_just_below_threshold_is_not_issue(self):
        m = healthy_metrics(cancel_return_count=14, total_order_count=100)  # 0.14
        assert check_high_cancel_rate(m) is None

    def test_zero_orders_holds_judgement(self):
        m = healthy_metrics(cancel_return_count=0, total_order_count=0)
        assert check_high_cancel_rate(m) is None


# ---------------------------------------------------------------------------
# HIGH_REFUND_RATE : 환불액 / 총 결제액 > 0.10
# ---------------------------------------------------------------------------
class TestHighRefundRate:
    def test_exactly_at_threshold_is_not_issue(self):
        m = healthy_metrics(refund_amount=100.0, total_payment_amount=1_000.0)  # 0.10
        assert check_high_refund_rate(m) is None

    def test_just_above_threshold_is_issue(self):
        m = healthy_metrics(refund_amount=101.0, total_payment_amount=1_000.0)
        assert check_high_refund_rate(m)["type"] == "HIGH_REFUND_RATE"

    def test_just_below_threshold_is_not_issue(self):
        m = healthy_metrics(refund_amount=99.0, total_payment_amount=1_000.0)
        assert check_high_refund_rate(m) is None

    def test_zero_payment_holds_judgement(self):
        m = healthy_metrics(refund_amount=0.0, total_payment_amount=0.0)
        assert check_high_refund_rate(m) is None


# ---------------------------------------------------------------------------
# LOW_REVENUE : 최근 30일 매출 < 카테고리별 최소 기준액
# ---------------------------------------------------------------------------
class TestLowRevenue:
    def test_exactly_at_threshold_is_not_issue(self):
        m = healthy_metrics(category="FASHION", revenue_30d=float(T.CATEGORY_MIN_REVENUE_30D["FASHION"]))
        assert check_low_revenue(m) is None

    def test_just_below_threshold_is_issue(self):
        m = healthy_metrics(category="FASHION", revenue_30d=T.CATEGORY_MIN_REVENUE_30D["FASHION"] - 1)
        assert check_low_revenue(m)["type"] == "LOW_REVENUE"

    def test_just_above_threshold_is_not_issue(self):
        m = healthy_metrics(category="FASHION", revenue_30d=T.CATEGORY_MIN_REVENUE_30D["FASHION"] + 1)
        assert check_low_revenue(m) is None

    def test_unknown_category_uses_default_threshold(self):
        m = healthy_metrics(category="NO_SUCH_CAT", revenue_30d=T.CATEGORY_MIN_REVENUE_DEFAULT - 1)
        assert check_low_revenue(m)["type"] == "LOW_REVENUE"

    def test_category_is_case_insensitive(self):
        m = healthy_metrics(category="fashion", revenue_30d=T.CATEGORY_MIN_REVENUE_30D["FASHION"] - 1)
        assert check_low_revenue(m) is not None


# ---------------------------------------------------------------------------
# NO_RECENT_ORDER : 최근 14일 신규 주문 0건
# ---------------------------------------------------------------------------
class TestNoRecentOrder:
    def test_new_orders_zero_is_issue(self):
        m = healthy_metrics(new_orders_14d=0)
        assert check_no_recent_order(m)["type"] == "NO_RECENT_ORDER"
        assert check_no_recent_order(m)["severity"] == 1.0

    def test_new_orders_one_is_not_issue(self):
        m = healthy_metrics(new_orders_14d=1)
        assert check_no_recent_order(m) is None

    def test_fallback_days_since_exactly_14_is_issue(self):
        m = healthy_metrics(new_orders_14d=None, days_since_last_order=14)
        assert check_no_recent_order(m)["type"] == "NO_RECENT_ORDER"

    def test_fallback_days_since_13_is_not_issue(self):
        m = healthy_metrics(new_orders_14d=None, days_since_last_order=13)
        assert check_no_recent_order(m) is None

    def test_fallback_days_since_15_is_issue(self):
        m = healthy_metrics(new_orders_14d=None, days_since_last_order=15)
        assert check_no_recent_order(m) is not None

    def test_no_signal_holds_judgement(self):
        m = healthy_metrics(new_orders_14d=None, days_since_last_order=None)
        assert check_no_recent_order(m) is None


# ---------------------------------------------------------------------------
# evaluate_seller : 종합점수 / 등급
# ---------------------------------------------------------------------------
class TestEvaluateSeller:
    def test_healthy_seller_scores_100_excellent(self):
        result = evaluate_seller(healthy_metrics())
        assert result["issues"] == []
        assert result["score"] == 100
        assert result["grade"] == "우수"

    def test_score_is_base_minus_weighted_penalty(self):
        # HIGH_CANCEL_RATE 하나만: rate 1.0 → severity 1.0 → 감점 = weight(25)
        m = healthy_metrics(cancel_return_count=100, total_order_count=100)
        result = evaluate_seller(m)
        assert [i["type"] for i in result["issues"]] == ["HIGH_CANCEL_RATE"]
        assert result["penalty"] == pytest.approx(T.ISSUE_WEIGHTS["HIGH_CANCEL_RATE"])
        assert result["score"] == 100 - T.ISSUE_WEIGHTS["HIGH_CANCEL_RATE"]
        assert result["grade"] == "주의"  # 75점

    def test_multi_issue_seller_is_at_risk(self):
        m = healthy_metrics(
            cancel_return_count=60, total_order_count=100,       # 60%
            refund_amount=500.0, total_payment_amount=1_000.0,   # 50%
            new_orders_14d=0,
            sales_count_30d=10.0, category_avg_sales_30d=500.0,  # ratio 0.02
            category="ETC", revenue_30d=0.0,
        )
        result = evaluate_seller(m)
        assert len(result["issues"]) >= 4
        assert result["score"] < T.GRADE_WARNING_MIN
        assert result["grade"] == "퇴출검토"

    def test_score_never_below_zero(self):
        m = healthy_metrics(
            sales_count_30d=0.0, category_avg_sales_30d=500.0,
            sales_7d=0.0, sales_prev_7d=100.0,
            cancel_return_count=100, total_order_count=100,
            refund_amount=1_000.0, total_payment_amount=1_000.0,
            revenue_30d=0.0,
            new_orders_14d=0,
        )
        result = evaluate_seller(m)
        assert result["score"] == 0
        assert result["grade"] == "퇴출검토"

    def test_grade_boundary_80_is_excellent(self):
        # 감점 정확히 20 → score 80
        m = healthy_metrics(refund_amount=1_000.0, total_payment_amount=1_000.0)  # rate 1.0 → penalty 20
        result = evaluate_seller(m)
        assert result["score"] == 80
        assert result["grade"] == "우수"

    def test_low_sales_uses_service_computed_category_avg(self):
        # evaluate_seller 는 dict 의 category_avg_sales_30d 를 그대로 신뢰한다.
        # (서비스 계층이 compute_category_avg_sales_30d 결과를 주입한다)
        m = healthy_metrics(sales_count_30d=10.0, category_avg_sales_30d=100.0)
        assert any(i["type"] == "LOW_SALES" for i in evaluate_seller(m)["issues"])

    def test_grade_boundary_50_is_warning(self):
        # HIGH_CANCEL(25) + HIGH_REFUND(20) + NO_RECENT_ORDER(10) 모두 severity 1.0 → penalty 55 → 45점
        # 여기서는 정확히 50점을 만들기 위해 조정: cancel severity 로 penalty 50 맞추기 어려우므로
        # NO_RECENT_ORDER(10) + HIGH_REFUND full(20) + HIGH_CANCEL full(25) - 5 는 불가.
        # 대신 두 규칙만: HIGH_REFUND(20) full + HIGH_CANCEL 부분(30점어치) 대신
        # HIGH_CANCEL_RATE full(25) + LOW_REVENUE full(15) + NO_RECENT_ORDER(10) = 50 → score 50
        m = healthy_metrics(
            cancel_return_count=100, total_order_count=100,  # penalty 25
            category="ETC", revenue_30d=0.0,                 # LOW_REVENUE full → penalty 15
            new_orders_14d=0,                                # penalty 10
        )
        result = evaluate_seller(m)
        assert result["penalty"] == pytest.approx(50.0)
        assert result["score"] == 50
        assert result["grade"] == "주의"


# ---------------------------------------------------------------------------
# compute_category_avg_sales_30d : 관심 셀러 목록 기준 카테고리 평균
# ---------------------------------------------------------------------------
class TestCategoryAvgSales:
    def test_simple_mean_per_category(self):
        rows = [
            {"category": "FASHION", "sales_count_30d": 100.0},
            {"category": "FASHION", "sales_count_30d": 300.0},
            {"category": "BEAUTY", "sales_count_30d": 50.0},
        ]
        avg = compute_category_avg_sales_30d(rows)
        assert avg["FASHION"] == 200.0
        assert avg["BEAUTY"] == 50.0

    def test_category_is_upper_cased(self):
        rows = [{"category": "fashion", "sales_count_30d": 10.0}]
        assert "FASHION" in compute_category_avg_sales_30d(rows)

    def test_missing_category_is_skipped(self):
        rows = [
            {"category": None, "sales_count_30d": 999.0},
            {"category": "", "sales_count_30d": 999.0},
            {"category": "FOOD", "sales_count_30d": 20.0},
        ]
        avg = compute_category_avg_sales_30d(rows)
        assert avg == {"FOOD": 20.0}

    def test_single_seller_category_avg_equals_self(self):
        # 카테고리에 셀러가 1명 → 평균 = 본인 값 → LOW_SALES 비율 1.0 → 미발동
        rows = [{"category": "DIGITAL", "sales_count_30d": 5.0, "sales_count_30d_dummy": 0}]
        avg = compute_category_avg_sales_30d(rows)
        assert avg["DIGITAL"] == 5.0
        m = {"category": "DIGITAL", "sales_count_30d": 5.0, "category_avg_sales_30d": avg["DIGITAL"]}
        assert check_low_sales(m) is None

    def test_empty_list(self):
        assert compute_category_avg_sales_30d([]) == {}
