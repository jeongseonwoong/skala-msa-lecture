// 셀러 운영 이슈 규칙 메타 정보 (기획안 2장 "조건 기반 이슈 규칙" 기준)
export const ISSUE_META = {
  LOW_SALES: {
    label: '판매 부진',
    icon: '📉',
    desc: '최근 30일 판매량이 카테고리 평균 대비 50% 미만입니다.'
  },
  SALES_DECLINING: {
    label: '판매량 하락',
    icon: '↘️',
    desc: '최근 7일 판매량이 이전 7일 대비 30% 이상 감소했습니다.'
  },
  HIGH_CANCEL_RATE: {
    label: '취소율 초과',
    icon: '🚫',
    desc: '취소·반품 비율이 기준치(15%)를 초과했습니다.'
  },
  HIGH_REFUND_RATE: {
    label: '환불율 초과',
    icon: '💸',
    desc: '환불 금액 비율이 기준치(10%)를 초과했습니다.'
  },
  LOW_REVENUE: {
    label: '매출 미달',
    icon: '⚠️',
    desc: '최근 30일 매출이 카테고리별 최소 유지 기준액에 못 미칩니다.'
  },
  NO_RECENT_ORDER: {
    label: '무주문 장기화',
    icon: '💤',
    desc: '최근 14일간 신규 주문이 없습니다.'
  }
}

// 종합 등급 메타 정보
export const GRADE_META = {
  EXCELLENT: { label: '우수', short: '우수 유지', cls: 'excellent' },
  WARNING: { label: '주의', short: '주의 관찰', cls: 'warning' },
  REVIEW: { label: '퇴출검토', short: '퇴출 검토', cls: 'review' },
  INSUFFICIENT: { label: '평가보류', short: '데이터 부족', cls: 'insufficient' }
}

// MD가 최종 확정하는 셀러 상태 (users.seller_status)
export const SELLER_STATUS_META = {
  ACTIVE: { label: '유지', cls: 'active' },
  WARNING: { label: '경고', cls: 'warning' },
  TERMINATED: { label: '퇴출', cls: 'terminated' }
}

// 상품 판매 상태
export const PRODUCT_STATUS_META = {
  ON_SALE: { label: '판매중', cls: 'on-sale' },
  SOLD_OUT: { label: '품절', cls: 'sold-out' },
  HIDDEN: { label: '판매중지', cls: 'hidden' }
}

export function severityLevel(severity) {
  const v = Number(severity ?? 0)
  if (v >= 0.66) return 'high'
  if (v >= 0.33) return 'mid'
  return 'low'
}
