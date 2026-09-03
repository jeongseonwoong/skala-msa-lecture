import api from './index.js'

// 백엔드는 강의 템플릿의 course-service(/api/courses)를 그대로 사용한다.
// (교수님 MSA 프로젝트를 최대한 수정하지 않는다는 전제 — 프론트에서만
//  course → product 로 도메인 매핑해서 호출한다.)
export const productApi = {
  getAll(params) {
    return api.get('/api/courses', { params })
  },
  getById(id) {
    return api.get(`/api/courses/${id}`)
  }
}
