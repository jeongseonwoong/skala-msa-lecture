"""course-service(상품 카탈로그) 내부 API 클라이언트.

호출 대상:
  GET {course_service_url}/api/courses/internal/seller/{sellerId}
  → [ {id, title, category, price, instructorId, enrollmentCount, status, ...}, ... ]
    (course-service 는 이 내부 엔드포인트를 래퍼 없이 배열로 반환)
"""

from __future__ import annotations

import logging
from typing import List

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 5.0


class CatalogServiceClient:
    def __init__(self) -> None:
        self.base_url = settings.course_service_url

    async def get_products_by_seller(self, seller_id: int) -> List[dict]:
        """셀러가 등록한 상품 목록. 실패 시 빈 리스트."""
        url = f"{self.base_url}/api/courses/internal/seller/{seller_id}"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
                response = await client.get(url)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            logger.error("[CatalogClient] 상품 목록 조회 실패 - sellerId=%s, error=%s", seller_id, exc)
            return []

        rows = body.get("data", body) if isinstance(body, dict) else body
        if not isinstance(rows, list):
            logger.error("[CatalogClient] 예상치 못한 응답 형태: %s", type(rows).__name__)
            return []
        return rows


catalog_client = CatalogServiceClient()
