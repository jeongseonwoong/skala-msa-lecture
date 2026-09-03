import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/views/LandingView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/callback',
    name: 'Callback',
    component: () => import('@/views/CallbackView.vue')
  },
  {
    path: '/md',
    name: 'MdDashboard',
    component: () => import('@/views/md/MdDashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/md/sellers',
    name: 'SellerRanking',
    component: () => import('@/views/md/SellerRankingView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/md/sellers/:id(\\d+)',
    name: 'SellerDetail',
    component: () => import('@/views/md/SellerDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/md/watchlist',
    name: 'MdWatchlist',
    component: () => import('@/views/md/MdWatchlistView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/mypage',
    name: 'MyPage',
    component: () => import('@/views/MdProfileView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 인증 가드 (이 서비스는 MD 전용 - 로그인하면 누구나 /md로)
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'Login' }
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'MdDashboard' }
  }
})

export default router
