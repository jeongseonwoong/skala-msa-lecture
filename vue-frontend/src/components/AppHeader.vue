<template>
  <header class="app-header">
    <div class="header-inner">
      <!-- 로고 -->
      <router-link to="/" class="logo">
        <span class="logo-mark"><RadarMark /></span>
        <span class="logo-text">SellerRadar</span>
      </router-link>

      <!-- 우측 액션 -->
      <div class="header-actions">
        <router-link to="/mypage" class="user-chip" :class="{ active: $route.path === '/mypage' }">
          <span class="user-avatar">{{ auth.user?.name?.charAt(0) || '?' }}</span>
          <span class="user-name">{{ auth.user?.name || 'MD' }}</span>
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/store/auth.js'
import RadarMark from '@/components/RadarMark.vue'

const auth = useAuthStore()
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
}
.header-inner {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 9px;
  flex-shrink: 0;
}
.logo-mark {
  width: 30px;
  height: 30px;
  padding: 6px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: #fff;
}
.logo-text {
  font-size: 16px;
  font-weight: 800;
  color: var(--color-text-primary);
  letter-spacing: -0.4px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}
.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px 5px 5px;
  border-radius: 999px;
  transition: var(--transition);
}
.user-chip:hover,
.user-chip.active {
  background: var(--color-bg-tertiary);
}
.user-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
}
</style>
