"""order-service(구 enrollment-service) 내부 API 클라이언트.

order-service 의 실제 필드명을 아는 코드는 이 파일 하나로 격리한다.
(evaluator / router / service 는 내부 모델 SellerMetrics 필드명에만 의존)

=====================================================================
 이 서비스가 호출하는 유일한 order-service 내부 API (assumed contract).
 응답 필드명 확정 후 _to_seller_metrics() 만 맞추면 된다.
---------------------------------------------------------------------
 GET /api/orders/internal/seller-metrics?watcherId={mdUserId}

   [A안 확정] order-service 가 watcherId(=MD user_id)로 필터링해서
   "그 MD 가 관심 셀러로 등록해 둔 셀러들"의 집계 지표만 반환한다.
   → recommend-service 는 이 1번 호출로 끝. 관심 셀러 목록을 따로 받지 않는다.

   - 집계값(30일 판매량, 취소율 등)은 order-service 가 계산해 완성값으로 내려준다.
     (categoryAvgSales30d 만 예외: 이 서비스가 계산한다. 아래 '확정된 사항' 참고)
   - "MD 가 관심 셀러를 등록/해제하는 화면·API"는 order-service(+프론트) 소관이고
     Sprint 1 범위 밖이다. 추천된 위험 셀러를 관심 목록에 넣을지는 MD 가 프론트에서
     직접 결정하며 recommend-service 와 무관하다.
     Sprint 1 데모에서는 관심 셀러 연결이 시드로 채워져 있다고 가정한다.

   - 응답 예시(가정):
       [
         {
           "sellerId": 1,
           "sellerName": "무지개상회",
           "category": "FASHION",
           "salesCount30d": 120,
           "sales7d": 18,
           "salesPrev7d": 40,
           "cancelReturnCount": 22,
           "totalOrderCount": 100,
           "refundAmount": 850000,
           "totalPaymentAmount": 7000000,
           "revenue30d": 6150000,
           "daysSinceLastOrder": 3,
           "newOrders14d": 12
         }
       ]

 확정된 사항:
   - 응답 필드/구조는 위 예시 그대로 사용한다.
   - sellerName 은 order-service 가 응답에 포함한다(user-service 별도 호출 안 함).
   - categoryAvgSales30d 는 order-service 가 주지 않는다. 이 서비스가 관심 셀러
     목록 안에서 카테고리별 평균을 계산한다(evaluator.compute_category_avg_sales_30d).

 미확정 항목(백엔드와 맞추면 되는 것):
   (1) 쿼리 파라미터명: 지금은 watcherId 로 보냄. order-service 가 읽는 이름과
       철자가 정확히 같아야 함(mdId / mdUserId / userId 등 후보).
   (2) 응답 래퍼 유무: 배열 그대로 vs { "data": [...] } — 클라이언트는 둘 다 처리함.
   (3) 개별 지표 필드명(salesCount30d 등) — _to_seller_metrics() 매핑만 수정하면 됨.
=====================================================================
"""

from __future__ import annotations

import logging
from typing import List

import httpx

from app.config.settings import settings
from app.model.schemas import SellerMetrics

logger = logging.getLogger(__name__)

_ASSUMED_PATH = "/api/orders/internal/seller-metrics"
_TIMEOUT_SECONDS = 5.0


def _to_seller_metrics(raw: dict) -> SellerMetrics:
    """order-service 응답(camelCase 1건) → 내부 모델(snake_case) 정규화.

    order-service 필드명 변경 시 수정 지점은 여기 한 곳뿐이다.
    """
    return SellerMetrics(
        seller_id=raw["sellerId"],
        seller_name=raw.get("sellerName"),
        category=raw.get("category"),
        sales_count_30d=raw.get("salesCount30d", 0.0),
        # category_avg_sales_30d 는 order-service 가 주지 않는다.
        # evaluation_service 에서 관심 셀러 목록 기준으로 계산해 채운다.
        sales_7d=raw.get("sales7d", 0.0),
        sales_prev_7d=raw.get("salesPrev7d", 0.0),
        cancel_return_count=raw.get("cancelReturnCount", 0),
        total_order_count=raw.get("totalOrderCount", 0),
        refund_amount=raw.get("refundAmount", 0.0),
        total_payment_amount=raw.get("totalPaymentAmount", 0.0),
        revenue_30d=raw.get("revenue30d", 0.0),
        days_since_last_order=raw.get("daysSinceLastOrder"),
        new_orders_14d=raw.get("newOrders14d"),
    )


class OrderServiceClient:
    def __init__(self) -> None:
        # 컨테이너 환경에서는 compose 가 ENROLLMENT_SERVICE_URL 만 주입하므로
        # settings.order_base_url 가 그 값을 재사용한다(settings.py 참고).
        self.base_url = settings.order_base_url

    async def get_watched_seller_metrics(self, md_user_id: int) -> List[SellerMetrics]:
        """MD 가 등록한 관심 셀러들의 집계 지표 조회.

        네트워크/파싱 실패 시 빈 리스트 반환(평가 엔진은 부분 실패에 강건해야 함).
        """
        url = f"{self.base_url}{_ASSUMED_PATH}"
        params = {"watcherId": md_user_id}

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            logger.error(
                "[OrderClient] seller-metrics 조회 실패 - watcherId=%s, error=%s",
                md_user_id,
                exc,
            )
            return []

        rows = body.get("data", body) if isinstance(body, dict) else body
        if not isinstance(rows, list):
            logger.error("[OrderClient] 예상치 못한 응답 형태: %s", type(rows).__name__)
            return []

        metrics: List[SellerMetrics] = []
        for raw in rows:
            try:
                metrics.append(_to_seller_metrics(raw))
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("[OrderClient] 지표 1건 파싱 스킵 - row=%s, error=%s", raw, exc)
        return metrics


order_client = OrderServiceClient()
