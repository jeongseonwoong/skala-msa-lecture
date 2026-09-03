<template>
  <aside class="sidebar">
    <div class="sidebar-section">
      <div class="sidebar-label">이슈 관리</div>

      <router-link to="/md" class="sidebar-item" :class="{ active: $route.path === '/md' }">
        <span class="si-icon">🏠</span> MD 홈
      </router-link>

      <router-link
        to="/md/sellers"
        class="sidebar-item"
        :class="{ active: $route.path.startsWith('/md/sellers') }"
      >
        <span class="si-icon">📊</span> 셀러 평가 랭킹
      </router-link>

      <router-link to="/md/watchlist" class="sidebar-item" :class="{ active: $route.path === '/md/watchlist' }">
        <span class="si-icon">⭐</span> 관심 셀러
        <span v-if="watchCount" class="sidebar-count">{{ watchCount }}</span>
      </router-link>
    </div>

    <div class="sidebar-section">
      <div class="sidebar-label">계정</div>
      <router-link to="/mypage" class="sidebar-item">
        <span class="si-icon">👤</span> 마이페이지
      </router-link>
      <button class="sidebar-item sidebar-btn" @click="handleLogout">
        <span class="si-icon">🚪</span> 로그아웃
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'
import { useEvaluationStore } from '@/store/evaluation.js'

const router = useRouter()
const auth = useAuthStore()
const evaluationStore = useEvaluationStore()

const watchCount = computed(() => evaluationStore.watchlist.length)

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 8px;
}
.sidebar-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  padding: 8px 12px 4px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--color-text-secondary);
  transition: var(--transition);
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-family: var(--font-sans);
  text-decoration: none;
}
.sidebar-item:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}
.sidebar-item.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 500;
}
.si-icon {
  font-size: 15px;
}
.sidebar-count {
  margin-left: auto;
  background: var(--color-primary);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 20px;
}
.sidebar-btn {
  color: var(--color-text-secondary);
}
</style>
