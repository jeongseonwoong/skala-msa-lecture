<template>
  <div class="landing">
    <AppHeader />

    <!-- 히어로 섹션 -->
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-content fade-in-up">
          <span class="hero-badge">MD를 위한 AI 셀러 운영 관리</span>
          <h1 class="hero-title">오늘 확인해야 할 셀러,<br>SellerRadar가 먼저 찾아드립니다</h1>
          <p class="hero-desc">
            판매·취소·환불 데이터를 규칙 기반으로 자동 채점하고, 리뷰·CS는 AI가 감성 분석해
            우선순위와 근거까지 함께 제시합니다.
          </p>
          <div class="hero-actions">
            <router-link to="/login" class="btn btn-primary btn-lg">MD로 시작하기</router-link>
          </div>
          <div class="hero-stats">
            <div class="stat"><span class="stat-num">6개</span><span class="stat-label">자동 이슈 탐지 규칙</span></div>
            <div class="stat"><span class="stat-num">3단계</span><span class="stat-label">셀러 등급 분류</span></div>
            <div class="stat"><span class="stat-num">AI</span><span class="stat-label">리뷰·CS 감성 분석</span></div>
          </div>
        </div>

        <!-- 제품 미리보기 카드 -->
        <div class="hero-preview fade-in">
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

    <!-- 특징 섹션 -->
    <section class="features-section">
      <div class="section-inner">
        <h2 class="section-title center">SellerRadar는 이렇게 동작합니다</h2>
        <div class="features-grid">
          <div v-for="f in features" :key="f.title" class="feature-card">
            <div class="feature-icon">{{ f.icon }}</div>
            <h3 class="feature-title">{{ f.title }}</h3>
            <p class="feature-desc">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="cta-inner">
        <h2>지금 바로 확인해보세요</h2>
        <p>MD 계정으로 로그인하면 전체 셀러 랭킹과 오늘의 이슈를 바로 볼 수 있습니다.</p>
        <router-link to="/login" class="btn btn-primary btn-lg">MD로 시작하기</router-link>
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
import AppHeader from '@/components/AppHeader.vue'
import GradeBadge from '@/components/md/GradeBadge.vue'
import IssueTag from '@/components/md/IssueTag.vue'

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
    issues: [
      { type: 'HIGH_REFUND_RATE', severity: 0.55 }
    ]
  }
]

const features = [
  { icon: '🧮', title: '규칙 기반 자동 채점', desc: '판매량·취소율·환불율·매출을 6개 조건 규칙으로 자동 검사해 이슈를 태깅합니다.' },
  { icon: '🤖', title: 'AI 리뷰·CS 감성 분석', desc: '리뷰 문맥을 분석해 가품 의심, CS 불친절 등 부정 언급 급증을 조기에 포착합니다.' },
  { icon: '📊', title: '우선순위 랭킹', desc: '퇴출검토 → 주의 순으로 정렬된 랭킹과 근거를 한 화면에서 확인합니다.' },
  { icon: '⭐', title: '관심 셀러 모니터링', desc: '밀착 추적이 필요한 셀러를 직접 등록해 지속적으로 관찰할 수 있습니다.' }
]
</script>

<style scoped>
.landing { background: var(--color-bg-secondary); }

/* 히어로 */
.hero {
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 50%, #f0f9ff 100%);
  border-bottom: 1px solid var(--color-border);
  padding: 80px 0 64px;
}
.hero-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 48px;
  align-items: center;
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
  font-size: 40px;
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: -0.5px;
  color: var(--color-text-primary);
  margin-bottom: 16px;
}
.hero-desc {
  font-size: 16px;
  color: var(--color-text-secondary);
  line-height: 1.7;
  max-width: 460px;
  margin-bottom: 28px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 40px;
}
.btn-lg { padding: 12px 28px; font-size: 15px; }
.hero-stats {
  display: flex;
  gap: 36px;
}
.stat { display: flex; flex-direction: column; gap: 2px; }
.stat-num { font-size: 22px; font-weight: 700; color: var(--color-primary); }
.stat-label { font-size: 12px; color: var(--color-text-secondary); }

/* 제품 미리보기 */
.hero-preview {
  width: 380px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
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
.preview-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px;
  border-radius: var(--radius-md);
}
.preview-row:hover { background: var(--color-bg-secondary); }
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
.features-section { padding: 64px 0; background: var(--color-bg-primary); }
.section-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.section-title { font-size: 22px; font-weight: 700; color: var(--color-text-primary); }
.section-title.center { text-align: center; margin-bottom: 40px; }
.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.feature-card {
  padding: 28px 24px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-align: center;
  transition: var(--transition);
}
.feature-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.feature-icon { font-size: 32px; margin-bottom: 12px; }
.feature-title { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
.feature-desc { font-size: 13px; color: var(--color-text-secondary); line-height: 1.6; }

/* CTA */
.cta-section {
  padding: 80px 0;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  text-align: center;
}
.cta-inner { max-width: 600px; margin: 0 auto; padding: 0 24px; }
.cta-inner h2 { font-size: 32px; font-weight: 700; color: #fff; margin-bottom: 12px; }
.cta-inner p { font-size: 16px; color: rgba(255,255,255,0.8); margin-bottom: 32px; }
.cta-inner .btn-primary {
  background: #fff;
  color: var(--color-primary);
  border-color: #fff;
  font-weight: 600;
}
.cta-inner .btn-primary:hover { background: #f0f7ff; }

/* 푸터 */
.footer {
  background: var(--color-text-primary);
  padding: 32px 0;
}
.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.footer-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
}
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
  .hero-preview { width: 100%; }
  .features-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .hero-title { font-size: 30px; }
  .features-grid { grid-template-columns: 1fr; }
  .footer-inner { flex-direction: column; gap: 12px; text-align: center; }
}
</style>
