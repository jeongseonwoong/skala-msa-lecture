"""셀러 운영 평가 엔진 - Pydantic 모델.

- SellerMetrics : order-service 응답을 정규화한 내부 지표 모델(snake_case).
                  외부(camelCase) → 내부 매핑은 app/client/order_client.py 에서만 처리.
- IssueDetail / SellerEvaluation / EvaluationResponse : 이 서비스가 프론트에 주는 응답 계약(camelCase).
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class IssueType(str, Enum):
    LOW_SALES = "LOW_SALES"
    SALES_DECLINING = "SALES_DECLINING"
    HIGH_CANCEL_RATE = "HIGH_CANCEL_RATE"
    HIGH_REFUND_RATE = "HIGH_REFUND_RATE"
    LOW_REVENUE = "LOW_REVENUE"
    NO_RECENT_ORDER = "NO_RECENT_ORDER"


class SellerGrade(str, Enum):
    EXCELLENT = "우수"
    WARNING = "주의"
    AT_RISK = "퇴출검토"


# ---------------------------------------------------------------------------
# 내부 지표 모델 (order-service ← 정규화 결과)
# ---------------------------------------------------------------------------

class SellerMetrics(BaseModel):
    """order-service 가 계산해서 내려주는 셀러별 집계 지표(정규화 후).

    이 서비스는 집계하지 않고 판정만 한다. 값이 없으면 0/None 으로 채워지고,
    비교 기준이 되는 값이 0/None 이면 해당 규칙은 판정 보류된다.
    """

    seller_id: int
    seller_name: Optional[str] = None
    category: Optional[str] = None

    # 판매량
    sales_count_30d: float = 0.0
    # order-service 가 주지 않음. evaluation_service 가 관심 셀러 목록에서 계산해 채운다.
    category_avg_sales_30d: float = 0.0
    sales_7d: float = 0.0
    sales_prev_7d: float = 0.0

    # 취소·반품
    cancel_return_count: int = 0
    total_order_count: int = 0

    # 환불
    refund_amount: float = 0.0
    total_payment_amount: float = 0.0

    # 매출 / 최근성
    revenue_30d: float = 0.0
    days_since_last_order: Optional[int] = None
    new_orders_14d: Optional[int] = None


# ---------------------------------------------------------------------------
# 응답 모델 (프론트 계약, camelCase)
# ---------------------------------------------------------------------------

class IssueDetail(BaseModel):
    type: IssueType
    severity: float = Field(ge=0.0, le=1.0)
    evidence: str


class SellerEvaluation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    seller_id: int = Field(alias="sellerId")
    seller_name: Optional[str] = Field(default=None, alias="sellerName")
    grade: SellerGrade
    score: int = Field(ge=0, le=100)
    issues: List[IssueDetail]


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    generated_at: datetime = Field(alias="generatedAt")
    sellers: List[SellerEvaluation]
