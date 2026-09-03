"""셀러 운영 평가 오케스트레이션.

order_client 로 지표를 받아 → evaluator 로 셀러별 판정 → 위험도 순 정렬.
Kafka / DB 를 사용하지 않으며, 요청마다 즉석 계산한다(무상태).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List

from app.client.order_client import order_client
from app.model.schemas import (
    EvaluationResponse,
    IssueDetail,
    SellerEvaluation,
)
from app.rules.evaluator import compute_category_avg_sales_30d, evaluate_seller

logger = logging.getLogger(__name__)


class EvaluationService:
    async def evaluate_watched_sellers(self, md_user_id: int) -> EvaluationResponse:
        metrics_list = await order_client.get_watched_seller_metrics(md_user_id)
        logger.info(
            "[EvaluationService] MD %s 관심 셀러 %d명 평가 시작",
            md_user_id,
            len(metrics_list),
        )

        rows = [m.model_dump() for m in metrics_list]

        # 카테고리 평균 판매량(LOW_SALES 기준)은 이 서비스가 관심 셀러 목록 안에서 계산
        category_avg = compute_category_avg_sales_30d(rows)

        evaluations: List[SellerEvaluation] = []
        for row in rows:
            category = str(row.get("category") or "").upper()
            row["category_avg_sales_30d"] = category_avg.get(category, 0.0)

            outcome = evaluate_seller(row)
            evaluations.append(
                SellerEvaluation(
                    seller_id=row["seller_id"],
                    seller_name=row.get("seller_name"),
                    grade=outcome["grade"],
                    score=outcome["score"],
                    issues=[IssueDetail(**issue) for issue in outcome["issues"]],
                )
            )

        # 위험도(=감점 penalty) 높은 셀러가 위로. score 오름차순과 동일하며,
        # 동점이면 이슈 많은 순. MD 가 먼저 봐야 할 셀러를 상단에 노출.
        evaluations.sort(key=lambda e: (e.score, -len(e.issues)))

        logger.info(
            "[EvaluationService] 평가 완료 - 총 %d명 (퇴출검토 %d명)",
            len(evaluations),
            sum(1 for e in evaluations if e.grade.value == "퇴출검토"),
        )

        return EvaluationResponse(
            generated_at=datetime.now(timezone.utc),
            sellers=evaluations,
        )


evaluation_service = EvaluationService()
