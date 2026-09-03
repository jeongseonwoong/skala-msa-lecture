import api from './index.js'

export const evaluationApi = {
  // 전체 셀러 평가 랭킹 조회 (MD용)
  // 게이트웨이는 /api/recommend/** 만 recommend-service로 라우팅하므로 그 아래로 붙인다.
  getSellers(params) {
    return api.get('/api/recommend/evaluation/sellers', { params })
  },

  // 셀러 단건 평가 상세 (지표·이슈·근거) - Sprint 2
  getSellerDetail(sellerId) {
    return api.get(`/api/recommend/evaluation/sellers/${sellerId}`)
  },

  // MD의 셀러 상태(유지/경고/퇴출) 확정 - Sprint 2 (게이트웨이 라우트/핸들러 미구현)
  updateSellerStatus(sellerId, status) {
    return api.patch(`/api/sellers/${sellerId}/status`, { status })
  }
}
