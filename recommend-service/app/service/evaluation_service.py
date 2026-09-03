"""셀러 운영 평가 오케스트레이션 (Sprint 1, 방식 B).

흐름:
  1. user-service     : 평가 대상 셀러 전체 목록
  2. course-service   : 셀러별 상품(가격·카테고리)
  3. order-service    : 셀러별 원시 주문 이력
  4. aggregator       : 셀러별 집계 지표(SellerMetrics)
  5. evaluator        : 규칙 판정 → 이슈 / 종합점수 / 등급
  6. 프론트 계약(camelCase, 한글 라벨)으로 변환해 배열 반환

Kafka / DB 미사용. 요청마다 즉석 계산(무상태).

Sprint 2 예정:
  - "MD 가 관심 셀러로 등록한 목록"만 평가 (지금은 전체 셀러)
  - payment-service 연동으로 매출·환불을 결제 데이터 기반으로 대체
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import List

from app.client.catalog_client import catalog_client
from app.client.order_client import order_client
from app.client.seller_client import seller_client
from app.model.schemas import (
    IssueOut,
    MetricsOut,
    SellerEvaluationOut,
    SellerGrade,
    SellerMetrics,
)
from app.rules import thresholds as T
from app.rules.aggregator import build_seller_metrics
from app.rules.evaluator import compute_category_avg_sales_30d, evaluate_seller

logger = logging.getLogger(__name__)

# evaluator 내부 등급(한글) → 프론트 등급 코드
_GRADE_CODE = {
    T.GRADE_EXCELLENT: SellerGrade.EXCELLENT,
    T.GRADE_WARNING: SellerGrade.WARNING,
    T.GRADE_AT_RISK: SellerGrade.REVIEW,
}

_INSUFFICIENT_NOTE = (
    "평가에 필요한 최소 주문 데이터(누적 {n}건)가 아직 쌓이지 않아 등급 산정을 보류합니다."
)


class EvaluationService:
    async def evaluate_all_sellers(self) -> List[SellerEvaluationOut]:
        sellers = await seller_client.get_all_sellers()
        logger.info("[EvaluationService] 평가 대상 셀러 %d명", len(sellers))
        if not sellers:
            return []

        # 셀러별 상품 + 주문 병렬 조회 후 집계
        metrics_list: List[SellerMetrics] = await asyncio.gather(
            *(self._collect_metrics(s) for s in sellers)
        )

        now = datetime.utcnow()
        rows = [m.model_dump() for m in metrics_list]
        category_avg = compute_category_avg_sales_30d(rows)

        results: List[SellerEvaluationOut] = []
        for m in metrics_list:
            cat = (m.category or "").upper()
            m.category_avg_sales_30d = category_avg.get(cat, 0.0)
            results.append(self._to_output(m))

        # MD 가 먼저 봐야 할 순서: 퇴출검토 > 주의 > 우수, 그 안에서 점수 낮은 순.
        # INSUFFICIENT(점수 없음)는 맨 뒤로.
        _order = {
            SellerGrade.REVIEW: 0,
            SellerGrade.WARNING: 1,
            SellerGrade.EXCELLENT: 2,
            SellerGrade.INSUFFICIENT: 3,
        }
        results.sort(key=lambda r: (_order[r.grade], r.score if r.score is not None else 999))
        logger.info(
            "[EvaluationService] 평가 완료 - 총 %d명 (퇴출검토 %d명)",
            len(results),
            sum(1 for r in results if r.grade == SellerGrade.REVIEW),
        )
        return results

    async def _collect_metrics(self, seller: dict) -> SellerMetrics:
        seller_id = seller.get("id")
        products, orders = await asyncio.gather(
            catalog_client.get_products_by_seller(seller_id),
            order_client.get_orders_by_seller(seller_id),
        )
        return build_seller_metrics(seller, products, orders)

    def _to_output(self, m: SellerMetrics) -> SellerEvaluationOut:
        cat = (m.category or "").upper()
        min_revenue = T.CATEGORY_MIN_REVENUE_30D.get(cat, T.CATEGORY_MIN_REVENUE_DEFAULT)
        metrics_out = MetricsOut(
            sales30d=m.sales_count_30d,
            categoryAvgSales30d=round(m.category_avg_sales_30d, 1),
            sales7d=m.sales_7d,
            salesPrev7d=m.sales_prev_7d,
            cancelRate=_rate_pct(m.cancel_return_count, m.total_order_count),
            refundRate=_rate_pct(m.refund_amount, m.total_payment_amount),
            revenue30d=m.revenue_30d,
            minRevenueThreshold=float(min_revenue),
            daysSinceLastOrder=m.days_since_last_order,
        )
        label = T.CATEGORY_LABELS.get(cat, m.category)

        # 데이터 부족 → 등급 보류
        if m.total_order_count < T.MIN_ORDERS_FOR_EVALUATION:
            return SellerEvaluationOut(
                id=m.seller_id,
                name=m.seller_name,
                category=label,
                grade=SellerGrade.INSUFFICIENT,
                score=None,
                sellerStatus=m.seller_status,
                joinedAt=m.joined_at,
                metrics=metrics_out,
                issues=[],
                insufficientNote=_INSUFFICIENT_NOTE.format(n=T.MIN_ORDERS_FOR_EVALUATION),
            )

        outcome = evaluate_seller(m.model_dump())
        issues = [
            IssueOut(type=i["type"], severity=i["severity"], detail=i["evidence"])
            for i in outcome["issues"]
        ]
        return SellerEvaluationOut(
            id=m.seller_id,
            name=m.seller_name,
            category=label,
            grade=_GRADE_CODE.get(outcome["grade"], SellerGrade.WARNING),
            score=outcome["score"],
            sellerStatus=m.seller_status,
            joinedAt=m.joined_at,
            metrics=metrics_out,
            issues=issues,
        )


def _rate_pct(numerator: float, denominator: float) -> float:
    if not denominator:
        return 0.0
    return round(numerator / denominator * 100, 1)


evaluation_service = EvaluationService()
