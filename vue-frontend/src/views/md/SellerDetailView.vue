<template>
  <div class="page-wrapper">
    <AppHeader />
    <div class="page-layout">
      <MdSidebar />

      <main class="main-content" v-if="seller">
        <router-link to="/sellers" class="back-link">← 셀러 평가 랭킹</router-link>

        <!-- 헤더 카드 -->
        <div class="detail-header fade-in-up">
          <div class="header-left">
            <div class="header-avatar" :class="`avatar-${seller.grade?.toLowerCase()}`">{{ seller.name.charAt(0) }}</div>
            <div>
              <div class="header-name-row">
                <h1 class="header-name">{{ seller.name }}</h1>
                <GradeBadge :grade="seller.grade" />
              </div>
              <p class="header-meta">{{ seller.category || '카테고리 미상' }}<template v-if="seller.joinedAt"> · 입점 {{ seller.joinedAt }}</template></p>
              <p v-if="seller.insufficientNote" class="insufficient-banner">ℹ️ {{ seller.insufficientNote }}</p>
            </div>
          </div>

          <div class="header-right">
            <div class="score-box">
              <span class="score-label">종합점수</span>
              <span class="score-value">{{ seller.score !== null ? seller.score : '-' }}</span>
            </div>
            <button
              class="star-btn-lg"
              :class="{ active: evaluationStore.isWatched(seller.id) }"
              @click="evaluationStore.toggleWatch(seller.id)"
            >
              {{ evaluationStore.isWatched(seller.id) ? '★ 관심 셀러' : '☆ 관심 셀러 등록' }}
            </button>
          </div>
        </div>

        <!-- MD 상태 확정 -->
        <section class="status-section">
          <div class="section-head-row">
            <h2 class="section-title">셀러 상태 확정</h2>
            <span class="status-current" :class="`status-${seller.sellerStatus?.toLowerCase()}`">
              현재: {{ statusLabel(seller.sellerStatus) }}
            </span>
          </div>
          <p class="section-desc">
            등급은 규칙 기반 <strong>권장</strong>이며, 최종 유지·경고·퇴출 여부는 MD가 확정합니다.
          </p>
          <div class="status-actions">
            <button class="status-btn status-btn-active" :disabled="seller.sellerStatus === 'ACTIVE'" @click="changeStatus('ACTIVE')">유지</button>
            <button class="status-btn status-btn-warning" :disabled="seller.sellerStatus === 'WARNING'" @click="changeStatus('WARNING')">경고</button>
            <button class="status-btn status-btn-terminated" :disabled="seller.sellerStatus === 'TERMINATED'" @click="changeStatus('TERMINATED')">퇴출</button>
          </div>
          <p class="status-helper">※ 상태 확정 API는 Sprint 2에서 연동됩니다. 지금은 화면에만 반영됩니다.</p>
        </section>

        <!-- 지표 그리드 -->
        <section v-if="seller.metrics">
          <h2 class="section-title">운영 지표</h2>
          <div class="metric-grid">
            <div class="metric-card" :class="{ 'metric-flag': hasIssue('LOW_SALES') }">
              <div class="metric-label">최근 30일 판매량</div>
              <div class="metric-value">{{ seller.metrics.sales30d }}건</div>
              <div class="metric-sub">카테고리 평균 {{ seller.metrics.categoryAvgSales30d }}건</div>
            </div>
            <div class="metric-card" :class="{ 'metric-flag': hasIssue('SALES_DECLINING') }">
              <div class="metric-label">최근 7일 판매량</div>
              <div class="metric-value">{{ seller.metrics.sales7d }}건</div>
              <div class="metric-sub">이전 7일 {{ seller.metrics.salesPrev7d }}건</div>
            </div>
            <div class="metric-card" :class="{ 'metric-flag': hasIssue('HIGH_CANCEL_RATE') }">
              <div class="metric-label">취소·반품율</div>
              <div class="metric-value">{{ formatPercent(seller.metrics.cancelRate) }}</div>
              <div class="metric-sub">기준 15% 이하</div>
            </div>
            <div class="metric-card" :class="{ 'metric-flag': hasIssue('HIGH_REFUND_RATE') }">
              <div class="metric-label">환불율</div>
              <div class="metric-value">{{ formatPercent(seller.metrics.refundRate) }}</div>
              <div class="metric-sub">기준 10% 이하</div>
            </div>
            <div class="metric-card" :class="{ 'metric-flag': hasIssue('LOW_REVENUE') }">
              <div class="metric-label">최근 30일 매출</div>
              <div class="metric-value">{{ formatWon(seller.metrics.revenue30d) }}</div>
              <div class="metric-sub">최소 유지 기준 {{ formatWon(seller.metrics.minRevenueThreshold) }}</div>
            </div>
            <div class="metric-card" :class="{ 'metric-flag': hasIssue('NO_RECENT_ORDER') }">
              <div class="metric-label">최근 주문</div>
              <div class="metric-value">{{ formatRelativeDays(seller.metrics.daysSinceLastOrder) }}</div>
              <div class="metric-sub">기준 14일 이내</div>
            </div>
          </div>
        </section>
        <section v-else>
          <h2 class="section-title">운영 지표</h2>
          <p class="empty-text">세부 지표는 아래 이슈 근거를 참고하세요. (지표 API는 준비 중입니다)</p>
        </section>

        <!-- 판매 상품 -->
        <section>
          <div class="section-head-row">
            <h2 class="section-title">판매 상품</h2>
            <span class="section-count">{{ products.length }}개</span>
          </div>
          <div v-if="productStore.loading" class="empty-text">불러오는 중...</div>
          <div v-else-if="products.length" class="product-list">
            <div v-for="product in products" :key="product.id" class="product-row">
              <div class="product-info">
                <span class="product-name">{{ product.name }}</span>
                <span class="product-category">{{ product.category }}</span>
              </div>
              <span class="product-price">{{ formatWon(product.price) }}</span>
              <span class="product-sales">누적 판매 {{ product.salesCount }}건</span>
              <span class="product-status" :class="`status-${productStatusMeta(product.status).cls}`">
                {{ productStatusMeta(product.status).label }}
              </span>
            </div>
          </div>
          <p v-else class="empty-text">등록된 상품이 없습니다.</p>
        </section>

        <!-- 이슈 근거 -->
        <section v-if="seller.issues.length">
          <h2 class="section-title">탐지된 이슈 근거</h2>
          <div class="issue-list">
            <div v-for="issue in sortedIssues" :key="issue.type" class="issue-card">
              <div class="issue-card-head">
                <IssueTag :issue="issue" />
                <span class="issue-severity">심각도 {{ Math.round(issue.severity * 100) }}%</span>
              </div>
              <div class="severity-bar"><div class="severity-fill" :class="`level-${severityLevel(issue.severity)}`" :style="{ width: issue.severity * 100 + '%' }"></div></div>
              <p class="issue-detail">{{ issue.detail }}</p>
            </div>
          </div>
        </section>
        <section v-else-if="seller.grade !== 'INSUFFICIENT'">
          <div class="no-issue-banner">✅ 현재 감지된 운영 이슈가 없습니다.</div>
        </section>

        <!-- 리뷰/CS 감성 분석 (Sprint 2: LLM 비정형 데이터 분석 연동 예정) -->
        <section v-if="seller.review">
          <h2 class="section-title">리뷰·CS 감성 분석 <span class="section-title-sub">(LLM 기반)</span></h2>
          <div class="review-panel">
            <div class="review-summary">
              <span>분석된 리뷰 {{ seller.review.totalReviews }}건</span>
            </div>

            <div class="review-columns">
              <div class="review-col">
                <div class="review-col-label negative">부정 언급 급증 카테고리</div>
                <div v-if="seller.review.negativeMentions.length" class="mention-list">
                  <div v-for="m in seller.review.negativeMentions" :key="m.tag" class="mention-chip negative">
                    <span class="mention-tag">{{ m.tag }}</span>
                    <span class="mention-count">{{ m.count }}건</span>
                    <span class="mention-trend">{{ m.trend }}</span>
                  </div>
                </div>
                <p v-else class="mention-empty">특이 부정 언급이 없습니다.</p>
              </div>

              <div class="review-col">
                <div class="review-col-label positive">긍정 언급</div>
                <div v-if="seller.review.positiveMentions.length" class="mention-list">
                  <div v-for="m in seller.review.positiveMentions" :key="m.tag" class="mention-chip positive">
                    <span class="mention-tag">{{ m.tag }}</span>
                    <span class="mention-count">{{ m.count }}건</span>
                  </div>
                </div>
                <p v-else class="mention-empty">아직 누적된 긍정 언급이 없습니다.</p>
              </div>
            </div>

            <blockquote class="sample-quote">"{{ seller.review.sampleQuote }}"</blockquote>
          </div>
        </section>
        <section v-else>
          <h2 class="section-title">리뷰·CS 감성 분석 <span class="section-title-sub">(LLM 기반)</span></h2>
          <div class="no-issue-banner" style="background:var(--color-bg-tertiary);color:var(--color-text-secondary);">
            리뷰·CS 비정형 데이터 감성 분석은 Sprint 2에서 연동됩니다.
          </div>
        </section>
      </main>

      <main class="main-content" v-else-if="evaluationStore.loading">
        <div class="loading-center"><div class="spinner"></div></div>
      </main>

      <main class="main-content" v-else>
        <p class="empty-text">셀러 정보를 찾을 수 없습니다.</p>
        <router-link to="/sellers" class="btn btn-primary" style="margin-top:16px;">랭킹으로 돌아가기</router-link>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import MdSidebar from '@/components/md/MdSidebar.vue'
import GradeBadge from '@/components/md/GradeBadge.vue'
import IssueTag from '@/components/md/IssueTag.vue'
import { useEvaluationStore } from '@/store/evaluation.js'
import { useProductStore } from '@/store/product.js'
import { formatWon, formatPercent, formatRelativeDays } from '@/utils/format.js'
import { severityLevel, SELLER_STATUS_META, PRODUCT_STATUS_META } from '@/constants/evaluation.js'

const route = useRoute()
const evaluationStore = useEvaluationStore()
const productStore = useProductStore()

const seller = computed(() => evaluationStore.getSellerById(route.params.id))
const products = computed(() => productStore.getProductsBySeller(route.params.id))

const sortedIssues = computed(() =>
  seller.value ? [...seller.value.issues].sort((a, b) => b.severity - a.severity) : []
)

function hasIssue(type) {
  return !!seller.value?.issues.some(i => i.type === type)
}

function statusLabel(status) {
  return SELLER_STATUS_META[status]?.label ?? status
}

function productStatusMeta(status) {
  return PRODUCT_STATUS_META[status] ?? { label: status, cls: 'on-sale' }
}

function changeStatus(status) {
  if (!seller.value) return
  evaluationStore.updateSellerStatus(seller.value.id, status)
}

onMounted(async () => {
  if (!evaluationStore.sellers.length) {
    await evaluationStore.fetchSellers()
  }
  if (!productStore.products.length) {
    await productStore.fetchProducts()
  }
})
</script>

<style scoped>
.page-wrapper {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.page-layout {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 24px;
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 28px;
}
.main-content {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.back-link {
  font-size: 13px;
  color: var(--color-text-secondary);
  transition: var(--transition);
}
.back-link:hover { color: var(--color-primary); }

/* 헤더 */
.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}
.header-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}
.header-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  flex-shrink: 0;
}
.avatar-excellent { background: var(--color-success-light); color: var(--color-success); }
.avatar-warning { background: var(--color-warning-light); color: var(--color-warning); }
.avatar-review { background: var(--color-danger-light); color: var(--color-danger); }
.avatar-insufficient { background: var(--color-neutral-light); color: var(--color-neutral); }

.header-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.header-name { font-size: 22px; font-weight: 700; color: var(--color-text-primary); }
.header-meta { font-size: 13px; color: var(--color-text-secondary); margin-top: 4px; }
.insufficient-banner {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-neutral);
  background: var(--color-neutral-light);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  max-width: 480px;
}

.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  flex-shrink: 0;
}
.score-box {
  text-align: right;
}
.score-label { display: block; font-size: 11px; color: var(--color-text-muted); }
.score-value { font-size: 30px; font-weight: 700; color: var(--color-primary); }
.star-btn-lg {
  padding: 7px 14px;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-primary);
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
}
.star-btn-lg.active {
  border-color: var(--color-star);
  color: var(--color-star);
  background: var(--color-star-light);
}

/* 상태 확정 */
.status-section {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  box-shadow: var(--shadow-sm);
}
.section-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}
.status-current {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}
.status-active { background: var(--color-success-light); color: var(--color-success); }
.status-warning { background: var(--color-warning-light); color: var(--color-warning); }
.status-terminated { background: var(--color-danger-light); color: var(--color-danger); }
.section-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 14px;
}
.status-actions {
  display: flex;
  gap: 10px;
}
.status-btn {
  padding: 9px 20px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-primary);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: var(--transition);
}
.status-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.status-btn-active:hover:not(:disabled) { border-color: var(--color-success); color: var(--color-success); }
.status-btn-warning:hover:not(:disabled) { border-color: var(--color-warning); color: var(--color-warning); }
.status-btn-terminated:hover:not(:disabled) { border-color: var(--color-danger); color: var(--color-danger); }
.status-helper {
  margin-top: 10px;
  font-size: 11px;
  color: var(--color-text-muted);
}

/* 공통 섹션 타이틀 */
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 14px;
}
.section-title-sub {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-muted);
}
.section-count {
  font-size: 12px;
  color: var(--color-text-muted);
  font-weight: 600;
}

/* 판매 상품 */
.product-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.product-row {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
}
.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.product-name { font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.product-category { font-size: 11px; color: var(--color-text-muted); }
.product-price { font-size: 13px; font-weight: 600; color: var(--color-text-primary); white-space: nowrap; }
.product-sales { font-size: 12px; color: var(--color-text-secondary); white-space: nowrap; }
.product-status {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  white-space: nowrap;
}
.product-status.status-on-sale { background: var(--color-success-light); color: var(--color-success); }
.product-status.status-sold-out { background: var(--color-neutral-light); color: var(--color-neutral); }
.product-status.status-hidden { background: var(--color-danger-light); color: var(--color-danger); }

/* 지표 그리드 */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.metric-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
}
.metric-flag {
  border-color: var(--color-danger);
  background: var(--color-danger-light);
}
.metric-label { font-size: 12px; color: var(--color-text-muted); margin-bottom: 6px; }
.metric-value { font-size: 20px; font-weight: 700; color: var(--color-text-primary); }
.metric-sub { font-size: 11px; color: var(--color-text-muted); margin-top: 4px; }

/* 이슈 근거 */
.issue-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.issue-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
}
.issue-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.issue-severity { font-size: 11px; color: var(--color-text-muted); font-weight: 600; }
.severity-bar {
  width: 100%;
  height: 6px;
  border-radius: 4px;
  background: var(--color-bg-tertiary);
  overflow: hidden;
  margin-bottom: 10px;
}
.severity-fill { height: 100%; border-radius: 4px; }
.severity-fill.level-high { background: var(--color-danger); }
.severity-fill.level-mid { background: var(--color-warning); }
.severity-fill.level-low { background: var(--color-text-muted); }
.issue-detail { font-size: 13px; color: var(--color-text-secondary); line-height: 1.6; }

.no-issue-banner {
  background: var(--color-success-light);
  color: var(--color-success);
  border-radius: var(--radius-md);
  padding: 14px 18px;
  font-size: 13px;
  font-weight: 500;
}

/* 리뷰 분석 */
.review-panel {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
}
.review-summary {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-bottom: 14px;
}
.review-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 16px;
}
.review-col-label {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 10px;
}
.review-col-label.negative { color: var(--color-danger); }
.review-col-label.positive { color: var(--color-success); }
.mention-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mention-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-size: 12px;
}
.mention-chip.negative { background: var(--color-danger-light); }
.mention-chip.positive { background: var(--color-success-light); }
.mention-tag { font-weight: 600; color: var(--color-text-primary); }
.mention-count { color: var(--color-text-secondary); }
.mention-trend { margin-left: auto; font-size: 11px; font-weight: 600; color: var(--color-danger); }
.mention-empty { font-size: 12px; color: var(--color-text-muted); }

.sample-quote {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-style: italic;
  border-left: 3px solid var(--color-border);
  padding-left: 14px;
  line-height: 1.6;
}

.empty-text { color: var(--color-text-muted); font-size: 14px; }

.loading-center {
  display: flex;
  justify-content: center;
  padding: 100px 0;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 992px) {
  .page-layout { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .detail-header { flex-direction: column; }
  .header-right { align-items: flex-start; }
  .metric-grid { grid-template-columns: 1fr 1fr; }
  .review-columns { grid-template-columns: 1fr; }
  .product-row { flex-wrap: wrap; }
}
</style>
