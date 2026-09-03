"""order-service(구 enrollment-service) 내부 API 클라이언트.

Sprint 1: 셀러 평가 엔진이 집계를 직접 한다(방식 B). 이 클라이언트는
셀러별 '원시 주문 이력'만 받아오고, 30일/7일 윈도우 집계는 app/rules/aggregator.py 가 한다.

호출 대상:
  GET {order_base_url}/api/enrollments/seller/{sellerId}
  → { "success": true, "data": [ {orderId, buyerId, productId, status, createdAt}, ... ] }
    (래퍼 없이 배열이 올 수도 있어 둘 다 처리)

  status ∈ COMPLETED | CANCELLED | RETURNED
"""

from __future__ import annotations

import logging
from typing import List

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 5.0


class OrderServiceClient:
    def __init__(self) -> None:
        # 컨테이너 환경에서는 ORDER_SERVICE_URL / ENROLLMENT_SERVICE_URL 로 주입된다.
        self.base_url = settings.order_base_url

    async def get_orders_by_seller(self, seller_id: int) -> List[dict]:
        """셀러의 상품에 걸린 모든 주문(상태 무관). 실패 시 빈 리스트."""
        url = f"{self.base_url}/api/enrollments/seller/{seller_id}"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
                response = await client.get(url)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            logger.error("[OrderClient] 주문 이력 조회 실패 - sellerId=%s, error=%s", seller_id, exc)
            return []

        rows = body.get("data", body) if isinstance(body, dict) else body
        if not isinstance(rows, list):
            logger.error("[OrderClient] 예상치 못한 응답 형태: %s", type(rows).__name__)
            return []
        return rows


order_client = OrderServiceClient()
