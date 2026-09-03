"""셀러 운영 평가 API 라우터.

GET /api/recommend/evaluation/sellers
  - 전체 셀러를 즉석 평가해 종합점수·등급·이슈를 위험도 순으로 반환 (Kafka / DB 미사용)
  - 응답: SellerEvaluationOut 배열 (래퍼 없음)

게이트웨이(SCG 4.2.0, 소스 없음)는 env 로 라우트 추가가 안 되므로 기존 /api/recommend/** 라우트를
재사용한다. 그래서 prefix 가 /api/recommend/evaluation 이다.
개발 중 직접 호출: http://localhost:8085/api/recommend/evaluation/sellers

Sprint 2 예정:
  - JWT/X-User-Id 로 MD 를 식별해 "그 MD 가 관심 셀러로 등록한 목록"만 평가
  - GET /api/recommend/evaluation/sellers/{sellerId} 단건 상세
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends

from app.config.security import verify_token
from app.model.schemas import SellerEvaluationOut
from app.service.evaluation_service import evaluation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recommend/evaluation", tags=["evaluation"])


@router.get("/sellers", response_model=List[SellerEvaluationOut])
async def evaluate_sellers(
    _token_payload: dict = Depends(verify_token),
) -> List[SellerEvaluationOut]:
    logger.info("[Router] 전체 셀러 평가 요청")
    return await evaluation_service.evaluate_all_sellers()


@router.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "UP", "service": "seller-evaluation"}
