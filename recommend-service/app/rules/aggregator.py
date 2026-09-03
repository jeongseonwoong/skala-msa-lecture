"""셀러별 원시 데이터(상품 + 주문) → 집계 지표(SellerMetrics).

Sprint 1 방식 B: payment-service 없이 '주문 상태 × 상품 가격'으로 매출·환불을 계산한다.
  - COMPLETED : 정상 판매 (매출)
  - RETURNED  : 반품 (결제됐다 환불 → 환불금액)
  - CANCELLED : 취소 (결제 안 됨)

순수 함수. 외부 I/O 없음.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import List, Optional

from app.model.schemas import SellerMetrics

_STATUS_COMPLETED = "COMPLETED"
_STATUS_RETURNED = "RETURNED"
_STATUS_CANCELLED = "CANCELLED"


def _parse_dt(value) -> Optional[datetime]:
    if not value:
        return None
    text = str(value)
    # Java LocalDateTime → "2026-08-15T13:45:30.123" / 초 단위 / 'Z' 등 방어
    text = text.replace("Z", "").split("+")[0]
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        try:
            return datetime.strptime(text[:19], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None


def _dominant_category(products: List[dict]) -> Optional[str]:
    cats = [str(p.get("category")).upper() for p in products if p.get("category")]
    if not cats:
        return None
    return Counter(cats).most_common(1)[0][0]


def build_seller_metrics(
    seller: dict,
    products: List[dict],
    orders: List[dict],
    now: Optional[datetime] = None,
) -> SellerMetrics:
    now = now or datetime.utcnow()
    d30, d14, d7 = now - timedelta(days=30), now - timedelta(days=14), now - timedelta(days=7)
    d7_prev_start = now - timedelta(days=14)

    price_by_product = {
        _to_int(p.get("id")): _to_float(p.get("price"))
        for p in products
        if p.get("id") is not None
    }

    sales_30d = sales_7d = sales_prev_7d = 0
    cancel_return = 0
    revenue_30d = refund_amount = paid_amount = 0.0
    new_orders_14d = 0
    last_order_at: Optional[datetime] = None

    for o in orders:
        status = str(o.get("status") or "").upper()
        created = _parse_dt(o.get("createdAt"))
        price = price_by_product.get(_to_int(o.get("productId")), 0.0)

        if created is not None:
            if last_order_at is None or created > last_order_at:
                last_order_at = created
            if created >= d14:
                new_orders_14d += 1

        if status == _STATUS_COMPLETED:
            paid_amount += price
            if created is not None and created >= d30:
                sales_30d += 1
                revenue_30d += price
            if created is not None and created >= d7:
                sales_7d += 1
            elif created is not None and d7_prev_start <= created < d7:
                sales_prev_7d += 1
        elif status == _STATUS_RETURNED:
            paid_amount += price
            refund_amount += price
            cancel_return += 1
        elif status == _STATUS_CANCELLED:
            cancel_return += 1

    days_since_last_order = (
        (now - last_order_at).days if last_order_at is not None else None
    )

    return SellerMetrics(
        seller_id=_to_int(seller.get("id")),
        seller_name=seller.get("name"),
        seller_status=seller.get("sellerStatus"),
        joined_at=_date_only(seller.get("createdAt")),
        category=_dominant_category(products),
        sales_count_30d=float(sales_30d),
        sales_7d=float(sales_7d),
        sales_prev_7d=float(sales_prev_7d),
        cancel_return_count=cancel_return,
        total_order_count=len(orders),
        refund_amount=refund_amount,
        total_payment_amount=paid_amount,
        revenue_30d=revenue_30d,
        days_since_last_order=days_since_last_order,
        new_orders_14d=new_orders_14d,
    )


def _to_int(value) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _date_only(value) -> Optional[str]:
    dt = _parse_dt(value)
    return dt.date().isoformat() if dt else (str(value)[:10] if value else None)
