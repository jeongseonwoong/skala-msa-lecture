<template>
  <div class="entry-page">
    <!-- 상단 로고 바 -->
    <header class="entry-header">
      <div class="entry-header-inner">
        <span class="logo-mark">📡</span>
        <span class="logo-text">SellerRadar</span>
      </div>
    </header>

    <!-- 히어로: 마케팅 소개 + 로그인/회원가입 -->
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-content fade-in-up">
          <span class="hero-badge">MD를 위한 AI 셀러 운영 관리</span>
          <h1 class="hero-title">오늘 확인해야 할 셀러,<br>SellerRadar가 먼저 찾아드립니다</h1>
          <p class="hero-desc">
            판매·취소·환불 데이터를 규칙 기반으로 자동 채점하고, 리뷰·CS는 AI가 감성 분석해
            우선순위와 근거까지 함께 제시합니다.
          </p>
          <ul class="feature-list">
            <li v-for="f in features" :key="f"><span class="dot"></span>{{ f }}</li>
          </ul>
          <div class="hero-stats">
            <div class="stat"><span class="stat-num">6개</span><span class="stat-label">자동 이슈 탐지 규칙</span></div>
            <div class="stat"><span class="stat-num">3단계</span><span class="stat-label">셀러 등급 분류</span></div>
            <div class="stat"><span class="stat-num">AI</span><span class="stat-label">리뷰·CS 감성 분석</span></div>
          </div>
        </div>

        <!-- 로그인 / 회원가입 카드 -->
        <div class="auth-card fade-in">
          <!-- 로그인 -->
          <div v-if="!showRegister" class="section">
            <h3 class="section-title">로그인</h3>
            <p class="section-desc">SellerRadar MD 계정으로 로그인합니다.</p>
            <button class="btn btn-primary btn-full" @click="handleOAuth">로그인</button>
            <div class="switch-link">
              계정이 없으신가요?
              <button class="text-btn" @click="showRegister = true">회원가입</button>
            </div>
          </div>

          <!-- 회원가입 -->
          <div v-else class="section">
            <h3 class="section-title">회원가입</h3>
            <form @submit.prevent="handleRegister" class="form">
              <div class="form-group">
                <label class="form-label">이름</label>
                <input v-model="registerForm.name" type="text" class="form-input" placeholder="홍길동" required />
              </div>
              <div class="form-group">
                <label class="form-label">이메일</label>
                <input v-model="registerForm.email" type="email" class="form-input" placeholder="user@example.com" required />
              </div>
              <div class="form-group">
                <label class="form-label">비밀번호</label>
                <input v-model="registerForm.password" type="password" class="form-input" placeholder="8자 이상" required />
              </div>
              <div v-if="error" class="error-msg">{{ error }}</div>
              <div v-if="success" class="success-msg">{{ success }}</div>
              <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
                <span v-if="loading">가입 중...</span>
                <span v-else>회원가입</span>
              </button>
            </form>
            <div class="switch-link">
              이미 계정이 있으신가요?
              <button class="text-btn" @click="showRegister = false">로그인</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 제품 미리보기 -->
    <section class="preview-section">
      <div class="section-inner">
        <h2 class="section-title-lg center">로그인하면 이렇게 보입니다</h2>
        <div class="preview-card">
          <div class="preview-header">
            <span class="preview-title">오늘 체크해야 할 셀러</span>
            <span class="preview-badge">3곳</span>
          </div>
          <div v-for="item in previewSellers" :key="item.name" class="preview-row">
            <div class="preview-avatar" :class="`avatar-${item.grade.toLowerCase()}`">{{ item.name.charAt(0) }}</div>
            <div class="preview-info">
              <div class="preview-name-row">
                <span class="preview-name">{{ item.name }}</span>
                <GradeBadge :grade="item.grade" />
              </div>
              <div class="preview-issues">
                <IssueTag v-for="issue in item.issues" :key="issue.type" :issue="issue" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 특징 -->
    <section class="features-section">
      <div class="section-inner">
        <h2 class="section-title-lg center">SellerRadar는 이렇게 동작합니다</h2>
        <div class="features-grid">
          <div v-for="f in featureCards" :key="f.title" class="feature-card">
            <div class="feature-icon">{{ f.icon }}</div>
            <h3 class="feature-title">{{ f.title }}</h3>
            <p class="feature-desc">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 푸터 -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-logo">
          <span class="footer-mark">📡</span>
          <span>SellerRadar</span>
        </div>
        <p class="footer-copy">© 2026 SellerRadar. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/store/auth.js'
import { authApi } from '@/api/auth.js'
import GradeBadge from '@/components/md/GradeBadge.vue'
import IssueTag from '@/components/md/IssueTag.vue'

const auth = useAuthStore()

const showRegister = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref('')

const registerForm = ref({ name: '', email: '', password: '', role: 'MD' })

const features = ['오늘 확인할 셀러 우선순위 제공', 'AI 리뷰·CS 감성 분석', '등급별 셀러 랭킹']

const previewSellers = [
  {
    name: '홈스타일마켓',
    grade: 'REVIEW',
    issues: [
      { type: 'NO_RECENT_ORDER', severity: 0.7 },
      { type: 'LOW_REVENUE', severity: 0.67 }
    ]
  },
  {
    name: '빈티지클로젯',
    grade: 'REVIEW',
    issues: [
      { type: 'HIGH_CANCEL_RATE', severity: 0.85 },
      { type: 'HIGH_REFUND_RATE', severity: 0.75 }
    ]
  },
  {
    name: '루미코스메틱',
    grade: 'WARNING',
    issues: [{ type: 'HIGH_REFUND_RATE', severity: 0.55 }]
  }
]

const featureCards = [
  { icon: '🧮', title: '규칙 기반 자동 채점', desc: '판매량·취소율·환불율·매출을 6개 조건 규칙으로 자동 검사해 이슈를 태깅합니다.' },
  { icon: '🤖', title: 'AI 리뷰·CS 감성 분석', desc: '리뷰 문맥을 분석해 가품 의심, CS 불친절 등 부정 언급 급증을 조기에 포착합니다.' },
  { icon: '📊', title: '우선순위 랭킹', desc: '퇴출검토 → 주의 순으로 정렬된 랭킹과 근거를 한 화면에서 확인합니다.' },
  { icon: '⭐', title: '관심 셀러 모니터링', desc: '밀착 추적이 필요한 셀러를 직접 등록해 지속적으로 관찰할 수 있습니다.' }
]

function handleOAuth() {
  auth.redirectToLogin()
}

async function handleRegister() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await authApi.register(registerForm.value)
    success.value = '회원가입 완료! 로그인 페이지로 이동합니다.'
    registerForm.value = { name: '', email: '', password: '', role: 'MD' }
    setTimeout(() => {
      showRegister.value = false
      success.value = ''
    }, 2000)
  } catch (e) {
    error.value = e.response?.data?.message || '회원가입에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.entry-page { background: var(--color-bg-secondary); }

/* 상단 로고 바 */
.entry-header {
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-primary);
}
.entry-header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo-mark {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.logo-text { font-size: 17px; font-weight: 700; color: var(--color-text-primary); letter-spacing: -0.3px; }

/* 히어로 */
.hero {
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 50%, #f0f9ff 100%);
  border-bottom: 1px solid var(--color-border);
  padding: 56px 0 64px;
}
.hero-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 48px;
  align-items: start;
}
.hero-badge {
  display: inline-block;
  padding: 5px 14px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 16px;
}
.hero-title {
  font-size: 36px;
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: -0.5px;
  color: var(--color-text-primary);
  margin-bottom: 14px;
}
.hero-desc {
  font-size: 15px;
  color: var(--color-text-secondary);
  line-height: 1.7;
  max-width: 460px;
  margin-bottom: 22px;
}
.feature-list { list-style: none; display: flex; flex-direction: column; gap: 10px; margin-bottom: 28px; }
.feature-list li { display: flex; align-items: center; gap: 10px; font-size: 14px; color: var(--color-text-secondary); }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--color-primary); flex-shrink: 0; }
.hero-stats { display: flex; gap: 32px; }
.stat { display: flex; flex-direction: column; gap: 2px; }
.stat-num { font-size: 20px; font-weight: 700; color: var(--color-primary); }
.stat-label { font-size: 12px; color: var(--color-text-secondary); }

/* 로그인 / 회원가입 카드 */
.auth-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 32px;
}
.section { display: flex; flex-direction: column; gap: 16px; }
.section-title { font-size: 20px; font-weight: 700; color: var(--color-text-primary); margin-bottom: 4px; }
.section-desc { font-size: 14px; color: var(--color-text-secondary); margin-bottom: 4px; }

.form { display: flex; flex-direction: column; gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; font-weight: 500; color: var(--color-text-secondary); }
.form-input {
  padding: 10px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-family: var(--font-sans);
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  transition: var(--transition);
  outline: none;
}
.form-input:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-light); }
.btn-full { width: 100%; padding: 12px; font-size: 15px; justify-content: center; margin-top: 4px; }

.switch-link {
  text-align: center;
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}
.text-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 0 2px;
  text-decoration: underline;
}
.error-msg {
  padding: 10px 14px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  font-size: 13px;
  color: #dc2626;
}
.success-msg {
  padding: 10px 14px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: var(--radius-md);
  font-size: 13px;
  color: #16a34a;
}

/* 공통 섹션 */
.section-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.section-title-lg { font-size: 22px; font-weight: 700; color: var(--color-text-primary); }
.section-title-lg.center { text-align: center; margin-bottom: 32px; }

/* 미리보기 */
.preview-section { padding: 64px 0; background: var(--color-bg-primary); }
.preview-card {
  max-width: 420px;
  margin: 0 auto;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 6px;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--color-border);
}
.preview-title { font-size: 13px; font-weight: 700; color: var(--color-text-primary); }
.preview-badge {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-danger);
  background: var(--color-danger-light);
  padding: 2px 8px;
  border-radius: 20px;
}
.preview-row { display: flex; align-items: flex-start; gap: 10px; padding: 8px; border-radius: var(--radius-md); }
.preview-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}
.avatar-review { background: var(--color-danger-light); color: var(--color-danger); }
.avatar-warning { background: var(--color-warning-light); color: var(--color-warning); }
.preview-info { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.preview-name-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.preview-name { font-size: 13px; font-weight: 600; color: var(--color-text-primary); }
.preview-issues { display: flex; gap: 4px; flex-wrap: wrap; }

/* 특징 */
.features-section { padding: 64px 0; }
.features-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.feature-card {
  padding: 28px 24px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-align: center;
  transition: var(--transition);
}
.feature-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.feature-icon { font-size: 32px; margin-bottom: 12px; }
.feature-title { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
.feature-desc { font-size: 13px; color: var(--color-text-secondary); line-height: 1.6; }

/* 푸터 */
.footer { background: var(--color-text-primary); padding: 32px 0; }
.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.footer-logo { display: flex; align-items: center; gap: 8px; color: #fff; font-size: 15px; font-weight: 600; }
.footer-mark {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: rgba(255,255,255,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.footer-copy { font-size: 13px; color: rgba(255,255,255,0.5); }

@media (max-width: 992px) {
  .hero-inner { grid-template-columns: 1fr; }
  .features-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .hero-title { font-size: 28px; }
  .features-grid { grid-template-columns: 1fr; }
  .footer-inner { flex-direction: column; gap: 12px; text-align: center; }
}
</style>
