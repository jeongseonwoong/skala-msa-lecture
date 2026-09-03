import { defineStore } from 'pinia'
import { ref } from 'vue'
import { productApi } from '@/api/product.js'
import { MOCK_SELLERS } from './evaluation.js'

function pick(obj, keys) {
  for (const k of keys) {
    if (obj[k] !== undefined && obj[k] !== null) return obj[k]
  }
  return undefined
}

function normalizeStatus(rawStatus) {
  const s = String(rawStatus ?? '').toUpperCase()
  if (s === 'SOLD_OUT') return 'SOLD_OUT'
  if (s === 'INACTIVE' || s === 'HIDDEN' || s === 'STOPPED') return 'HIDDEN'
  return 'ON_SALE'
}

// course-service 응답을 product 도메인으로 매핑.
// 원본 템플릿 필드명이 snake_case/camelCase가 섞여있어 방어적으로 여러 키를 시도한다.
function normalizeProduct(course) {
  const sellerId = pick(course, ['instructorId', 'instructor_id', 'instructor', 'teacherId', 'teacher_id'])
  const sellerName = pick(course, ['instructorName', 'instructor_name', 'teacherName', 'teacher_name', 'ownerName'])
  const salesCount = pick(course, ['enrollment_count', 'enrollmentCount']) ?? 0

  return {
    id: course.id,
    name: course.title,
    category: course.category,
    price: Number(course.price ?? 0),
    status: normalizeStatus(course.status),
    salesCount: Number(salesCount),
    sellerId: sellerId !== undefined ? Number(sellerId) : null,
    sellerName: sellerName ?? null
  }
}

// ↓↓↓ MOCK FALLBACK — /api/courses 연동 완료되면 이 함수와 evaluation.js의
// MOCK_SELLERS를 통째로 지우면 된다.
function mockProducts() {
  return MOCK_SELLERS.flatMap((s) =>
    (s.products || []).map((p) => ({ ...p, sellerId: s.id, sellerName: s.name }))
  )
}
// ↑↑↑ MOCK FALLBACK 끝

export const useProductStore = defineStore('product', () => {
  const products = ref([])
  const loading = ref(false)

  async function fetchProducts() {
    loading.value = true

    try {
      const res = await productApi.getAll()
      console.log('[ProductStore] /api/courses response =', res.data)

      const raw = Array.isArray(res.data?.data)
        ? res.data.data
        : Array.isArray(res.data)
          ? res.data
          : []

      if (!raw.length) throw new Error('empty response')

      products.value = raw.map(normalizeProduct)
    } catch (e) {
      console.warn('[ProductStore] /api/courses 연동 실패 - 목업 상품으로 대체합니다:', e.message)
      products.value = mockProducts()
    } finally {
      loading.value = false
    }
  }

  function getProductsBySeller(sellerId) {
    return products.value.filter((p) => String(p.sellerId) === String(sellerId))
  }

  return { products, loading, fetchProducts, getProductsBySeller }
})
