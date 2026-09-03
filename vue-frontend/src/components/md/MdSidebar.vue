<template>
  <aside class="sidebar">
    <nav class="sidebar-nav">
      <div class="sidebar-section">
        <div class="sidebar-label">이슈 관리</div>

        <router-link to="/" class="sidebar-item" :class="{ active: $route.path === '/' }">
          <span class="si-icon">🏠</span> MD 홈
        </router-link>

        <router-link
          to="/sellers"
          class="sidebar-item"
          :class="{ active: $route.path.startsWith('/sellers') }"
        >
          <span class="si-icon">📊</span> 셀러 평가 랭킹
        </router-link>

        <router-link to="/products" class="sidebar-item" :class="{ active: $route.path === '/products' }">
          <span class="si-icon">🛒</span> 전체 상품
        </router-link>

        <router-link to="/watchlist" class="sidebar-item" :class="{ active: $route.path === '/watchlist' }">
          <span class="si-icon">⭐</span> 관심 셀러
          <span v-if="watchCount" class="sidebar-count">{{ watchCount }}</span>
        </router-link>
      </div>

      <div class="sidebar-section">
        <div class="sidebar-label">계정</div>
        <router-link to="/mypage" class="sidebar-item" :class="{ active: $route.path === '/mypage' }">
          <span class="si-icon">👤</span> 마이페이지
        </router-link>
        <button class="sidebar-item sidebar-btn" @click="handleLogout">
          <span class="si-icon">🚪</span> 로그아웃
        </button>
      </div>
    </nav>
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
  position: sticky;
  top: 92px;
  align-self: start;
}
.sidebar-nav {
  background: var(--color-chrome-bg);
  border-radius: var(--radius-lg);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: var(--shadow-md);
}
.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 4px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-chrome-border);
}
.sidebar-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}
.sidebar-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--color-chrome-text-muted);
  padding: 6px 10px 8px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: var(--radius-md);
  font-size: 13.5px;
  font-weight: 500;
  color: var(--color-chrome-text);
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
  background: var(--color-chrome-bg-hover);
  color: var(--color-chrome-text-active);
}
.sidebar-item.active {
  background: var(--color-chrome-active-bg);
  color: var(--color-chrome-text-active);
  font-weight: 600;
}
.si-icon {
  font-size: 15px;
  width: 18px;
  text-align: center;
  flex-shrink: 0;
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
</style>
