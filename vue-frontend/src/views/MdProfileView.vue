<template>
  <div class="page-wrapper">
    <AppHeader />
    <div class="page-layout">
      <MdSidebar />

      <main class="main-content">
        <h1 class="page-title">마이페이지</h1>

        <div class="profile-card fade-in-up">
          <div class="profile-avatar">{{ auth.user?.name?.charAt(0) || '?' }}</div>
          <div class="profile-info">
            <h2 class="profile-name">{{ auth.user?.name || 'MD' }}</h2>
            <p class="profile-email">{{ auth.user?.email || '-' }}</p>
            <span class="badge badge-md">MD</span>
          </div>
        </div>

        <section class="activity-section">
          <h3 class="section-title">내 활동 요약</h3>
          <div class="summary-cards">
            <div class="summary-card">
              <div class="summary-label">관리 중인 전체 셀러</div>
              <div class="summary-value">{{ evaluationStore.sellers.length }}</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">등록한 관심 셀러</div>
              <div class="summary-value">{{ evaluationStore.watchlist.length }}</div>
            </div>
            <div class="summary-card summary-danger">
              <div class="summary-label">확인이 필요한 셀러</div>
              <div class="summary-value">{{ evaluationStore.priorityQueue.length }}</div>
            </div>
          </div>
        </section>

        <button class="btn btn-ghost logout-btn" @click="handleLogout">로그아웃</button>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import MdSidebar from '@/components/md/MdSidebar.vue'
import { useAuthStore } from '@/store/auth.js'
import { useEvaluationStore } from '@/store/evaluation.js'

const router = useRouter()
const auth = useAuthStore()
const evaluationStore = useEvaluationStore()

function handleLogout() {
  auth.logout()
  router.push('/')
}

onMounted(() => {
  if (!evaluationStore.sellers.length) {
    evaluationStore.fetchSellers()
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
.main-content {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 28px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: var(--shadow-sm);
}
.profile-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.profile-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.profile-name { font-size: 20px; font-weight: 700; }
.profile-email { font-size: 14px; color: var(--color-text-secondary); }
.badge-md {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 14px;
}
.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.summary-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
}
.summary-danger .summary-value { color: var(--color-danger); }
.summary-label {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-bottom: 8px;
}
.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.logout-btn {
  align-self: flex-start;
}

@media (max-width: 992px) {
  .page-layout { grid-template-columns: 1fr; }
  .summary-cards { grid-template-columns: 1fr; }
}
</style>
