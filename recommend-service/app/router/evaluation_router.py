"""셀러 운영 평가 API 라우터.

GET /api/evaluation/sellers
  - JWT 에서 MD 의 user_id 를 추출 → 그 MD 가 등록한 관심 셀러를 즉석 평가
  - 종합점수·등급·이슈를 위험도 순으로 반환 (Kafka / DB 미사용)

MD user_id 획득 방식:
  1순위) 게이트웨이가 주입하는 X-User-Id 헤더 (course/enrollment/payment 서비스와 동일 방식)
  2순위) JWT payload 의 sub / userId 클레임 (게이트웨이 없이 :8085 직접 호출하는 개발 상황)

TODO(백엔드/게이트웨이 협의):
  - api-gateway 가 /api/evaluation/** 를 이 서비스로 라우팅하도록 route 추가 필요.
    (기존엔 /api/recommend/** 만 매핑되어 있을 가능성이 큼. Eureka service-id 는
     "recommend-service" 그대로 유지했으므로 predicates 의 Path 만 추가하면 됨.)
    개발 중 직접 테스트는 http://localhost:8085/api/evaluation/sellers 로 가능.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.config.security import verify_token
from app.model.schemas import EvaluationResponse
from app.service.evaluation_service import evaluation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


def _resolve_md_user_id(x_user_id: Optional[int], token_payload: dict) -> int:
    if x_user_id is not None:
        return x_user_id

    raw = (
        token_payload.get("sub")
        or token_payload.get("userId")
        or token_payload.get("user_id")
    )
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MD user_id 를 확인할 수 없습니다 (X-User-Id 헤더 또는 토큰 sub 필요)",
        )


@router.get("/sellers", response_model=EvaluationResponse)
async def evaluate_sellers(
    x_user_id: Optional[int] = Header(default=None, alias="X-User-Id"),
    token_payload: dict = Depends(verify_token),
) -> EvaluationResponse:
    md_user_id = _resolve_md_user_id(x_user_id, token_payload)
    logger.info("[Router] 셀러 평가 요청 - mdUserId=%s", md_user_id)
    return await evaluation_service.evaluate_watched_sellers(md_user_id)


@router.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "UP", "service": "seller-evaluation"}
