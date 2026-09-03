<template>
  <div class="page-wrapper">
    <AppHeader />
    <div class="page-layout">
      <MdSidebar />

      <main class="main-content">
        <div class="content-header">
          <div>
            <h1 class="page-title">셀러 평가 랭킹</h1>
            <p class="page-subtitle">조건 규칙으로 산출된 종합점수·등급 순으로 전체 셀러를 확인합니다.</p>
          </div>
        </div>

        <!-- 필터 -->
        <div class="filter-bar">
          <button
            v-for="g in gradeFilters"
            :key="g.value"
            class="filter-chip"
            :class="{ active: selectedGrade === g.value }"
            @click="selectedGrade = g.value"
          >
            {{ g.label }}
            <span class="chip-count">{{ gradeFilterCount(g.value) }}</span>
          </button>

          <div class="filter-spacer"></div>

          <input
            v-model="keyword"
            type="text"
            class="search-input"
            placeholder="셀러명 검색"
          />

          <select v-model="sortKey" class="sort-select">
            <option value="score-asc">종합점수 낮은순</option>
            <option value="score-desc">종합점수 높은순</option>
            <option value="cancelRate-desc">취소율 높은순</option>
            <option value="refundRate-desc">환불율 높은순</option>
            <option value="revenue-asc">매출 낮은순</option>
          </select>
        </div>

        <div v-if="evaluationStore.loading" class="loading-center">
          <div class="spinner"></div>
        </div>

        <div v-else-if="sortedSellers.length" class="seller-table fade-in">
          <div class="table-header">
            <span class="col-rank">#</span>
            <span class="col-seller">셀러</span>
            <span class="col-grade">등급</span>
            <span class="col-score">종합점수</span>
            <span class="col-issues">이슈</span>
            <span class="col-metrics">주요 지표</span>
            <span class="col-action"></span>
          </div>

          <div v-for="(seller, idx) in sortedSellers" :key="seller.id" class="seller-row">
            <span class="col-rank">{{ idx + 1 }}</span>

            <div class="col-seller">
              <div class="row-avatar" :class="`avatar-${seller.grade?.toLowerCase()}`">{{ seller.name.charAt(0) }}</div>
              <div class="row-id-text">
                <div class="row-name">
                  {{ seller.name }}
                  <button
                    class="star-btn"
                    :class="{ active: evaluationStore.isWatched(seller.id) }"
                    :title="evaluationStore.isWatched(seller.id) ? '관심 셀러 해제' : '관심 셀러 등록'"
                    @click="evaluationStore.toggleWatch(seller.id)"
                  >
                    {{ evaluationStore.isWatched(seller.id) ? '★' : '☆' }}
                  </button>
                </div>
                <div class="row-category">{{ seller.category }} · 입점 {{ seller.joinedAt }}</div>
              </div>
            </div>

            <div class="col-grade"><GradeBadge :grade="seller.grade" /></div>

            <div class="col-score">
              <template v-if="seller.score !== null">
                <div class="score-bar"><div class="score-fill" :style="{ width: seller.score + '%' }" :class="scoreClass(seller.grade)"></div></div>
                <span class="score-text">{{ seller.score }}점</span>
              </template>
              <span v-else class="score-na">평가 보류</span>
            </div>

            <div class="col-issues">
              <template v-if="seller.issues.length">
                <IssueTag v-for="issue in seller.issues.slice(0, 2)" :key="issue.type" :issue="issue" />
                <span v-if="seller.issues.length > 2" class="more-issues">+{{ seller.issues.length - 2 }}</span>
              </template>
              <span v-else-if="seller.grade === 'INSUFFICIENT'" class="no-issue">데이터 누적 중</span>
              <span v-else class="no-issue">이슈 없음</span>
            </div>

            <div class="col-metrics">
              <span>매출 {{ formatWon(seller.metrics.revenue30d) }}</span>
              <span>취소 {{ formatPercent(seller.metrics.cancelRate) }}</span>
              <span>환불 {{ formatPercent(seller.metrics.refundRate) }}</span>
            </div>

            <div class="col-action">
              <router-link :to="`/md/sellers/${seller.id}`" class="btn btn-ghost btn-sm">상세보기</router-link>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <p>조건에 맞는 셀러가 없습니다.</p>
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
import IssueTag from '@/components/md/IssueTag.vue'
import { useEvaluationStore } from '@/store/evaluation.js'
import { formatWon, formatPercent } from '@/utils/format.js'

const evaluationStore = useEvaluationStore()

const selectedGrade = ref('ALL')
const keyword = ref('')
const sortKey = ref('score-asc')

const gradeFilters = [
  { value: 'ALL', label: '전체' },
  { value: 'EXCELLENT', label: '우수' },
  { value: 'WARNING', label: '주의' },
  { value: 'REVIEW', label: '퇴출검토' },
  { value: 'INSUFFICIENT', label: '평가보류' }
]

function gradeFilterCount(value) {
  if (value === 'ALL') return evaluationStore.sellers.length
  return evaluationStore.gradeCounts[value] ?? 0
}

function scoreClass(grade) {
  if (grade === 'EXCELLENT') return 'fill-excellent'
  if (grade === 'WARNING') return 'fill-warning'
  return 'fill-review'
}

const filteredSellers = computed(() => {
  let list = evaluationStore.sellers
  if (selectedGrade.value !== 'ALL') {
    list = list.filter(s => s.grade === selectedGrade.value)
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    list = list.filter(s => s.name.toLowerCase().includes(kw))
  }
  return list
})

const sortedSellers = computed(() => {
  const list = [...filteredSellers.value]
  const [field, dir] = sortKey.value.split('-')

  list.sort((a, b) => {
    let av, bv
    if (field === 'score') { av = a.score ?? -1; bv = b.score ?? -1 }
    else if (field === 'cancelRate') { av = a.metrics.cancelRate; bv = b.metrics.cancelRate }
    else if (field === 'refundRate') { av = a.metrics.refundRate; bv = b.metrics.refundRate }
    else if (field === 'revenue') { av = a.metrics.revenue30d; bv = b.metrics.revenue30d }

    return dir === 'asc' ? av - bv : bv - av
  })

  return list
})

onMounted(() => {
  evaluationStore.fetchSellers()
})
</script>

<style scoped>
.page-wrapper {
  min-height: 100vh;
  background: var(--color-bg-secondary);
}
.page-layout {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 24px;
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 28px;
}
.main-content {
  min-width: 0;
}

.content-header {
  margin-bottom: 20px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
}
.page-subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: var(--color-text-muted);
}

/* 필터바 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
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
.chip-count {
  font-size: 11px;
  opacity: 0.85;
}
.filter-spacer { flex: 1; }
.search-input {
  padding: 8px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 13px;
  font-family: var(--font-sans);
  width: 180px;
  outline: none;
}
.search-input:focus { border-color: var(--color-primary); }
.sort-select {
  padding: 8px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 13px;
  font-family: var(--font-sans);
  color: var(--color-text-secondary);
  background: var(--color-bg-primary);
  outline: none;
  cursor: pointer;
}

/* 테이블 */
.seller-table {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-x: auto;
}
.table-header,
.seller-row {
  display: grid;
  grid-template-columns: 24px 200px 90px 110px minmax(120px, 1fr) 170px 76px;
  align-items: center;
  gap: 10px;
  min-width: 880px;
}
.table-header {
  padding: 0 18px 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.seller-row {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
  transition: var(--transition);
}
.seller-row:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--color-border-hover);
}

.col-rank { font-size: 13px; font-weight: 700; color: var(--color-text-muted); }

.col-seller {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.row-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}
.avatar-excellent { background: var(--color-success-light); color: var(--color-success); }
.avatar-warning { background: var(--color-warning-light); color: var(--color-warning); }
.avatar-review { background: var(--color-danger-light); color: var(--color-danger); }
.avatar-insufficient { background: var(--color-neutral-light); color: var(--color-neutral); }

.row-id-text { min-width: 0; }
.row-name {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.row-category {
  font-size: 11px;
  color: var(--color-text-muted);
  white-space: nowrap;
}
.star-btn {
  background: none;
  border: none;
  font-size: 15px;
  color: var(--color-border-hover);
  cursor: pointer;
  line-height: 1;
}
.star-btn.active,
.star-btn:hover { color: #f5a623; }

.col-score {
  display: flex;
  align-items: center;
  gap: 8px;
}
.score-bar {
  width: 56px;
  height: 6px;
  border-radius: 4px;
  background: var(--color-bg-tertiary);
  overflow: hidden;
}
.score-fill { height: 100%; border-radius: 4px; }
.fill-excellent { background: var(--color-success); }
.fill-warning { background: var(--color-warning); }
.fill-review { background: var(--color-danger); }
.score-text { font-size: 12px; font-weight: 600; color: var(--color-text-secondary); white-space: nowrap; }
.score-na { font-size: 12px; color: var(--color-text-muted); }

.col-issues {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  min-width: 0;
}
.more-issues { font-size: 11px; color: var(--color-text-muted); }
.no-issue { font-size: 12px; color: var(--color-text-muted); }

.col-metrics {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 11px;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.col-action { display: flex; justify-content: flex-end; }
.btn-sm { padding: 6px 12px; font-size: 12px; white-space: nowrap; }

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
