<template>
  <div class="page-wrapper">
    <AppHeader />
    <div class="page-layout">
      <MdSidebar />

      <main class="main-content">
        <div class="content-header">
          <div>
            <h1 class="page-title">관심 셀러</h1>
            <p class="page-subtitle">지속적인 주의가 필요하다고 판단해 직접 등록한 셀러 목록입니다.</p>
          </div>
        </div>

        <div v-if="evaluationStore.loading" class="loading-center">
          <div class="spinner"></div>
        </div>

        <div v-else-if="watchedSellers.length" class="watch-list fade-in">
          <div v-for="seller in watchedSellers" :key="seller.id" class="watch-card">
            <div class="watch-id">
              <div class="watch-avatar" :class="`avatar-${seller.grade?.toLowerCase()}`">{{ seller.name.charAt(0) }}</div>
              <div>
                <div class="watch-name-row">
                  <router-link :to="`/sellers/${seller.id}`" class="watch-name">{{ seller.name }}</router-link>
                  <GradeBadge :grade="seller.grade" />
                </div>
                <div class="watch-meta">{{ seller.category || '카테고리 미상' }} · 종합점수 {{ seller.score ?? '-' }}점</div>
              </div>
            </div>

            <div class="watch-issues">
              <template v-if="seller.issues.length">
                <IssueTag v-for="issue in seller.issues.slice(0, 3)" :key="issue.type" :issue="issue" />
              </template>
              <span v-else class="no-issue">이슈 없음</span>
            </div>

            <div class="watch-actions">
              <router-link :to="`/sellers/${seller.id}`" class="btn btn-ghost btn-sm">상세보기</router-link>
              <button class="btn btn-outline btn-sm" @click="evaluationStore.toggleWatch(seller.id)">등록 해제</button>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <p class="empty-icon">⭐</p>
          <p>아직 등록한 관심 셀러가 없습니다.</p>
          <p class="empty-sub">셀러 평가 랭킹에서 ☆ 버튼을 눌러 밀착 모니터링할 셀러를 등록하세요.</p>
          <router-link to="/sellers" class="btn btn-primary" style="margin-top:16px;">셀러 평가 랭킹으로 이동</router-link>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import MdSidebar from '@/components/md/MdSidebar.vue'
import GradeBadge from '@/components/md/GradeBadge.vue'
import IssueTag from '@/components/md/IssueTag.vue'
import { useEvaluationStore } from '@/store/evaluation.js'

const evaluationStore = useEvaluationStore()

const watchedSellers = computed(() =>
  evaluationStore.sellers.filter(s => evaluationStore.isWatched(s.id))
)

onMounted(async () => {
  if (!evaluationStore.sellers.length) {
    await evaluationStore.fetchSellers()
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

.content-header { margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: 700; color: var(--color-text-primary); }
.page-subtitle { margin-top: 6px; font-size: 13px; color: var(--color-text-muted); }

.watch-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.watch-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  transition: var(--transition);
}
.watch-card:hover { box-shadow: var(--shadow-sm); }

.watch-id {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 220px;
}
.watch-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
  flex-shrink: 0;
}
.avatar-excellent { background: var(--color-success-light); color: var(--color-success); }
.avatar-warning { background: var(--color-warning-light); color: var(--color-warning); }
.avatar-review { background: var(--color-danger-light); color: var(--color-danger); }
.avatar-insufficient { background: var(--color-neutral-light); color: var(--color-neutral); }

.watch-name-row { display: flex; align-items: center; gap: 8px; }
.watch-name { font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.watch-meta { font-size: 12px; color: var(--color-text-muted); margin-top: 2px; }

.watch-issues {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.no-issue { font-size: 12px; color: var(--color-text-muted); }

.watch-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-sm { padding: 7px 14px; font-size: 12px; white-space: nowrap; }

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: var(--color-text-muted);
}
.empty-icon { font-size: 44px; margin-bottom: 12px; }
.empty-sub { font-size: 13px; margin-top: 4px; }

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
  .watch-card { flex-wrap: wrap; }
}
</style>
