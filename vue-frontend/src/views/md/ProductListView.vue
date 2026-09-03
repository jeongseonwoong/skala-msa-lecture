<template>
  <div class="page-wrapper">
    <AppHeader />
    <div class="page-layout">
      <MdSidebar />

      <main class="main-content">
        <div class="content-header">
          <div>
            <h1 class="page-title">전체 상품</h1>
            <p class="page-subtitle">모든 셀러가 등록한 상품을 한 곳에서 확인합니다.</p>
          </div>
        </div>

        <!-- 필터 -->
        <div class="filter-bar">
          <button
            v-for="s in statusFilters"
            :key="s.value"
            class="filter-chip"
            :class="{ active: selectedStatus === s.value }"
            @click="selectedStatus = s.value"
          >
            {{ s.label }}
          </button>

          <div class="filter-spacer"></div>

          <input v-model="keyword" type="text" class="search-input" placeholder="상품명 · 셀러명 검색" />
        </div>

        <div v-if="productStore.loading" class="loading-center">
          <div class="spinner"></div>
        </div>

        <div v-else-if="filteredProducts.length" class="product-table fade-in">
          <div class="table-header">
            <span class="col-product">상품</span>
            <span class="col-seller">셀러</span>
            <span class="col-price">가격</span>
            <span class="col-sales">누적 판매</span>
            <span class="col-status">상태</span>
          </div>

          <div v-for="product in filteredProducts" :key="`${product.sellerId}-${product.id}`" class="product-row">
            <div class="col-product">
              <div class="product-name">{{ product.name }}</div>
              <div class="product-category">{{ product.category }}</div>
            </div>

            <router-link :to="`/sellers/${product.sellerId}`" class="col-seller seller-link">
              <span class="seller-name">{{ product.sellerName }}</span>
              <GradeBadge :grade="product.sellerGrade" />
            </router-link>

            <span class="col-price">{{ formatWon(product.price) }}</span>
            <span class="col-sales">{{ product.salesCount }}건</span>

            <span class="col-status">
              <span class="status-badge" :class="`status-${statusMeta(product.status).cls}`">
                {{ statusMeta(product.status).label }}
              </span>
            </span>
          </div>
        </div>

        <div v-else class="empty-state">
          <p>조건에 맞는 상품이 없습니다.</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import MdSidebar from '@/components/md/MdSidebar.vue'
import GradeBadge from '@/components/md/GradeBadge.vue'
import { useEvaluationStore } from '@/store/evaluation.js'
import { useProductStore } from '@/store/product.js'
import { formatWon } from '@/utils/format.js'
import { PRODUCT_STATUS_META } from '@/constants/evaluation.js'

const evaluationStore = useEvaluationStore()
const productStore = useProductStore()

const selectedStatus = ref('ALL')
const keyword = ref('')

const statusFilters = [
  { value: 'ALL', label: '전체' },
  { value: 'ON_SALE', label: '판매중' },
  { value: 'SOLD_OUT', label: '품절' },
  { value: 'HIDDEN', label: '판매중지' }
]

function statusMeta(status) {
  return PRODUCT_STATUS_META[status] ?? { label: status, cls: 'on-sale' }
}

// 상품(course-service)과 셀러 평가(evaluation-service) 응답을 sellerId로 조인
const productsWithSeller = computed(() =>
  productStore.products.map((p) => {
    const seller = evaluationStore.getSellerById(p.sellerId)
    return {
      ...p,
      sellerName: p.sellerName || seller?.name || '알 수 없음',
      sellerGrade: seller?.grade || 'INSUFFICIENT'
    }
  })
)

const filteredProducts = computed(() => {
  let list = productsWithSeller.value

  if (selectedStatus.value !== 'ALL') {
    list = list.filter((p) => p.status === selectedStatus.value)
  }

  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    list = list.filter(
      (p) => p.name.toLowerCase().includes(kw) || p.sellerName.toLowerCase().includes(kw)
    )
  }

  return list
})

onMounted(() => {
  if (!evaluationStore.sellers.length) {
    evaluationStore.fetchSellers()
  }
  if (!productStore.products.length) {
    productStore.fetchProducts()
  }
})
</script>

<style scoped>
.page-wrapper {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.page-layout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 28px;
}
.main-content { min-width: 0; }

.content-header { margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { margin-top: 6px; font-size: 13px; color: var(--color-text-muted); }

/* 필터바 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.filter-chip {
  padding: 7px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-primary);
  color: var(--color-text-secondary);
  transition: var(--transition);
  cursor: pointer;
}
.filter-chip:hover { border-color: var(--color-primary); color: var(--color-primary); }
.filter-chip.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.filter-spacer { flex: 1; }
.search-input {
  padding: 8px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 13px;
  font-family: var(--font-sans);
  width: 220px;
  outline: none;
}
.search-input:focus { border-color: var(--color-primary); }

/* 테이블 */
.product-table {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-x: auto;
}
.table-header,
.product-row {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) 200px 110px 100px 90px;
  align-items: center;
  gap: 14px;
  min-width: 760px;
}
.table-header {
  padding: 0 18px 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.product-row {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
  transition: var(--transition);
}
.product-row:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--color-border-hover);
}

.product-name { font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.product-category { font-size: 11px; color: var(--color-text-muted); margin-top: 2px; }

.seller-link {
  display: flex;
  align-items: center;
  gap: 8px;
}
.seller-name { font-size: 13px; font-weight: 500; color: var(--color-text-primary); }
.seller-link:hover .seller-name { color: var(--color-primary); }

.col-price, .col-sales { font-size: 13px; color: var(--color-text-secondary); }

.status-badge {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.status-badge.status-on-sale { background: var(--color-success-light); color: var(--color-success); }
.status-badge.status-sold-out { background: var(--color-neutral-light); color: var(--color-neutral); }
.status-badge.status-hidden { background: var(--color-danger-light); color: var(--color-danger); }

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: var(--color-text-muted);
}

.loading-center {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 992px) {
  .page-layout { grid-template-columns: 1fr; }
}
</style>
