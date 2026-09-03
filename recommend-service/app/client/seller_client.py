"""user-service(회원) 내부 API 클라이언트.

호출 대상:
  GET {user_service_url}/api/users/internal/sellers
  → [ {id, email, name, role, sellerStatus, createdAt}, ... ]   (role == SELLER 만)
    (user-service 는 이 내부 엔드포인트를 래퍼 없이 배열로 반환)

Sprint 2: "MD 가 관심 셀러로 등록한 목록"만 필터링하는 버전으로 교체 예정.
"""

from __future__ import annotations

import logging
from typing import List

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 5.0


class SellerServiceClient:
    def __init__(self) -> None:
        self.base_url = settings.user_service_url

    async def get_all_sellers(self) -> List[dict]:
        """평가 대상 셀러 전체. 실패 시 빈 리스트."""
        url = f"{self.base_url}/api/users/internal/sellers"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
                response = await client.get(url)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            logger.error("[SellerClient] 셀러 목록 조회 실패 - error=%s", exc)
            return []

        rows = body.get("data", body) if isinstance(body, dict) else body
        if not isinstance(rows, list):
            logger.error("[SellerClient] 예상치 못한 응답 형태: %s", type(rows).__name__)
            return []
        return rows


seller_client = SellerServiceClient()
