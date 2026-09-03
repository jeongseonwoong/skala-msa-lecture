"""셀러 운영 평가 엔진 - Pydantic 모델.

- SellerMetrics : course/order/user 서비스 응답을 집계한 내부 지표 모델(snake_case).
                  집계 로직은 app/rules/aggregator.py, 외부 호출은 app/client/* 에서 처리.
- MetricsOut / IssueOut / SellerEvaluationOut : 프론트(vue-frontend)에 주는 응답 계약(camelCase).
  이 서비스는 래퍼 없이 SellerEvaluationOut 배열을 그대로 반환한다.
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
    """프론트 GRADE_META 키와 일치시킨다(constants/evaluation.js)."""
    EXCELLENT = "EXCELLENT"      # 우수
    WARNING = "WARNING"          # 주의
    REVIEW = "REVIEW"            # 퇴출검토
    INSUFFICIENT = "INSUFFICIENT"  # 평가보류(데이터 부족)


# ---------------------------------------------------------------------------
# 내부 지표 모델 (course/order/user ← 집계 결과)
# ---------------------------------------------------------------------------

class SellerMetrics(BaseModel):
    """셀러별 집계 지표(정규화 후). 값이 없으면 0/None 으로 채워지고,
    비교 기준이 되는 값이 0/None 이면 해당 규칙은 판정 보류된다."""

    seller_id: int
    seller_name: Optional[str] = None
    seller_status: Optional[str] = None
    joined_at: Optional[str] = None
    category: Optional[str] = None

    # 판매량
    sales_count_30d: float = 0.0
    category_avg_sales_30d: float = 0.0  # aggregator 가 아닌 evaluation_service 에서 채운다
    sales_7d: float = 0.0
    sales_prev_7d: float = 0.0

    # 취소·반품
    cancel_return_count: int = 0
    total_order_count: int = 0

    # 환불 / 매출
    refund_amount: float = 0.0
    total_payment_amount: float = 0.0
    revenue_30d: float = 0.0

    # 최근성
    days_since_last_order: Optional[int] = None
    new_orders_14d: Optional[int] = None


# ---------------------------------------------------------------------------
# 응답 모델 (프론트 계약, camelCase)
# ---------------------------------------------------------------------------

class IssueOut(BaseModel):
    type: IssueType
    severity: float = Field(ge=0.0, le=1.0)
    detail: str


class MetricsOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sales30d: float = Field(alias="sales30d")
    category_avg_sales_30d: float = Field(alias="categoryAvgSales30d")
    sales7d: float = Field(alias="sales7d")
    sales_prev_7d: float = Field(alias="salesPrev7d")
    cancel_rate: float = Field(alias="cancelRate")          # 퍼센트 (예: 18.7)
    refund_rate: float = Field(alias="refundRate")          # 퍼센트
    revenue30d: float = Field(alias="revenue30d")
    min_revenue_threshold: float = Field(alias="minRevenueThreshold")
    days_since_last_order: Optional[int] = Field(default=None, alias="daysSinceLastOrder")


class SellerEvaluationOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: Optional[str] = None
    category: Optional[str] = None          # 프론트 표시용 한글 라벨
    grade: SellerGrade
    score: Optional[int] = Field(default=None, ge=0, le=100)
    seller_status: Optional[str] = Field(default=None, alias="sellerStatus")
    joined_at: Optional[str] = Field(default=None, alias="joinedAt")
    metrics: MetricsOut
    issues: List[IssueOut]
    insufficient_note: Optional[str] = Field(default=None, alias="insufficientNote")


# 참고: 응답은 List[SellerEvaluationOut] 를 그대로 반환한다(래퍼 없음).
class EvaluationMeta(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    generated_at: datetime = Field(alias="generatedAt")
