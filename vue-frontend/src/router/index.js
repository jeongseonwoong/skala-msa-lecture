import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'

const routes = [
  {
    // 로그인 상태: MD 홈(오늘 체크할 셀러). 비로그인 상태: /login으로 리다이렉트
    path: '/',
    name: 'MdDashboard',
    component: () => import('@/views/md/MdDashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    // 비로그인 첫 진입: 랜딩 소개 + 로그인/회원가입이 합쳐진 화면
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
    path: '/sellers',
    name: 'SellerRanking',
    component: () => import('@/views/md/SellerRankingView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/sellers/:id(\\d+)',
    name: 'SellerDetail',
    component: () => import('@/views/md/SellerDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/products',
    name: 'ProductList',
    component: () => import('@/views/md/ProductListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/watchlist',
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

// 인증 가드 (이 서비스는 MD 전용 - 로그인하면 누구나 /로)
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
