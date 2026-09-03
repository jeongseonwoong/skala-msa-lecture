<template>
  <div class="page-wrapper">
    <AppHeader />
    <div class="page-layout">
      <MdSidebar />

      <main class="main-content">
        <div class="content-header">
          <div>
            <h1 class="page-title">
              안녕하세요, {{ auth.user?.name || "MD" }}님
            </h1>
            <p class="page-subtitle">
              {{ todayLabel }} 기준, 확인이 필요한 셀러는
              <strong>{{ priorityCount }}곳</strong>입니다.
            </p>
          </div>
          <router-link to="/sellers" class="btn btn-outline"
            >전체 랭킹 보기</router-link
          >
        </div>

        <!-- 요약 통계 -->
        <div class="stat-grid">
          <div class="stat-card">
            <span class="stat-icon">🏬</span>
            <div>
              <div class="stat-value">{{ evaluationStore.sellers.length }}</div>
              <div class="stat-label">전체 관리 셀러</div>
            </div>
          </div>
          <div class="stat-card stat-danger">
            <span class="stat-icon">🚨</span>
            <div>
              <div class="stat-value">
                {{ evaluationStore.gradeCounts.REVIEW }}
              </div>
              <div class="stat-label">퇴출검토</div>
            </div>
          </div>
          <div class="stat-card stat-warning">
            <span class="stat-icon">⚠️</span>
            <div>
              <div class="stat-value">
                {{ evaluationStore.gradeCounts.WARNING }}
              </div>
              <div class="stat-label">주의</div>
            </div>
          </div>
          <div class="stat-card">
            <span class="stat-icon">⭐</span>
            <div>
              <div class="stat-value">
                {{ evaluationStore.watchlist.length }}
              </div>
              <div class="stat-label">관심 셀러</div>
            </div>
          </div>
        </div>

        <!-- 오늘 체크해야 할 셀러 -->
        <section class="priority-section">
          <div class="section-head">
            <h2 class="section-title">오늘 체크해야 할 셀러</h2>
            <span class="section-subtitle"
              >퇴출검토 → 주의 순, 점수가 낮은 셀러부터 정렬됩니다.</span
            >
          </div>

          <div v-if="evaluationStore.loading" class="loading-center">
            <div class="spinner"></div>
          </div>

          <div v-else-if="displayedQueue.length" class="priority-list fade-in">
            <div
              v-for="(seller, idx) in displayedQueue"
              :key="seller.id"
              class="priority-card"
            >
              <div class="pc-rank">{{ idx + 1 }}</div>

              <div class="pc-id">
                <div
                  class="pc-avatar"
                  :class="`avatar-${seller.grade?.toLowerCase()}`"
                >
                  {{ seller.name.charAt(0) }}
                </div>
                <div>
                  <div class="pc-name-row">
                    <router-link
                      :to="`/sellers/${seller.id}`"
                      class="pc-name"
                      >{{ seller.name }}</router-link
                    >
                    <GradeBadge :grade="seller.grade" />
                  </div>
                  <div class="pc-meta">
                    {{ seller.category }} · 종합점수 {{ seller.score ?? "-" }}점
                  </div>
                </div>
              </div>

              <div class="pc-issues">
                <IssueTag
                  v-for="issue in topIssues(seller)"
                  :key="issue.type"
                  :issue="issue"
                />
                <span v-if="seller.issues.length > 2" class="more-issues"
                  >+{{ seller.issues.length - 2 }}건 더</span
                >
                <span
                  v-if="seller.grade === 'INSUFFICIENT'"
                  class="insufficient-note"
                  >{{ seller.insufficientNote }}</span
                >
              </div>

              <div class="pc-actions">
                <button
                  class="star-btn"
                  :class="{ active: evaluationStore.isWatched(seller.id) }"
                  :title="
                    evaluationStore.isWatched(seller.id)
                      ? '관심 셀러 해제'
                      : '관심 셀러 등록'
                  "
                  @click="evaluationStore.toggleWatch(seller.id)"
                >
                  {{ evaluationStore.isWatched(seller.id) ? "★" : "☆" }}
                </button>
                <router-link
                  :to="`/sellers/${seller.id}`"
                  class="btn btn-primary btn-sm"
                  >상세 확인</router-link
                >
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <p class="empty-icon">✅</p>
            <p>오늘 특별히 확인이 필요한 셀러가 없습니다.</p>
          </div>

          <div
            v-if="evaluationStore.priorityQueue.length > displayedQueue.length"
            class="show-more-row"
          >
            <button class="btn btn-ghost" @click="showAll = true">
              나머지
              {{
                evaluationStore.priorityQueue.length - displayedQueue.length
              }}곳 더 보기
            </button>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import AppHeader from "@/components/AppHeader.vue";
import MdSidebar from "@/components/md/MdSidebar.vue";
import GradeBadge from "@/components/md/GradeBadge.vue";
import IssueTag from "@/components/md/IssueTag.vue";
import { useAuthStore } from "@/store/auth.js";
import { useEvaluationStore } from "@/store/evaluation.js";

const auth = useAuthStore();
const evaluationStore = useEvaluationStore();

const showAll = ref(false);

const priorityCount = computed(() => evaluationStore.priorityQueue.length);
const displayedQueue = computed(() =>
  showAll.value
    ? evaluationStore.priorityQueue
    : evaluationStore.priorityQueue.slice(0, 6),
);

const todayLabel = computed(() => {
  const d = new Date();
  return `${d.getMonth() + 1}월 ${d.getDate()}일`;
});

function topIssues(seller) {
  return [...seller.issues].sort((a, b) => b.severity - a.severity).slice(0, 2);
}

onMounted(() => {
  evaluationStore.fetchSellers();
});
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
.main-content {
  min-width: 0;
}

.content-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
}
.page-subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
}
.page-subtitle strong {
  color: var(--color-danger);
}

/* 요약 통계 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 32px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
}
.stat-icon {
  font-size: 24px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}
.stat-label {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 2px;
}
.stat-danger .stat-value {
  color: var(--color-danger);
}
.stat-warning .stat-value {
  color: var(--color-warning);
}

/* 우선순위 섹션 */
.section-head {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
}
.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
}
.section-subtitle {
  font-size: 12px;
  color: var(--color-text-muted);
}

.priority-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.priority-card {
  display: grid;
  grid-template-columns: 32px minmax(220px, 280px) 1fr auto;
  align-items: center;
  gap: 18px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  transition: var(--transition);
}
.priority-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-border-hover);
}
.pc-rank {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-muted);
  text-align: center;
}
.pc-id {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}
.pc-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}
.avatar-excellent {
  background: var(--color-success-light);
  color: var(--color-success);
}
.avatar-warning {
  background: var(--color-warning-light);
  color: var(--color-warning);
}
.avatar-review {
  background: var(--color-danger-light);
  color: var(--color-danger);
}
.avatar-insufficient {
  background: var(--color-neutral-light);
  color: var(--color-neutral);
}

.pc-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.pc-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.pc-meta {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.pc-issues {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  min-width: 0;
}
.more-issues {
  font-size: 11px;
  color: var(--color-text-muted);
}
.insufficient-note {
  font-size: 12px;
  color: var(--color-neutral);
  font-style: italic;
}

.pc-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.star-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--color-border-hover);
  cursor: pointer;
  line-height: 1;
  transition: var(--transition);
}
.star-btn.active,
.star-btn:hover {
  color: var(--color-star);
}
.btn-sm {
  padding: 7px 14px;
  font-size: 13px;
  white-space: nowrap;
}

.show-more-row {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--color-text-muted);
}
.empty-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.loading-center {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 992px) {
  .page-layout {
    grid-template-columns: 1fr;
  }
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .priority-card {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .pc-rank {
    display: none;
  }
  .pc-actions {
    justify-content: flex-end;
  }
}
</style>
