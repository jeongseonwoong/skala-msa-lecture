import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { evaluationApi } from "@/api/evaluation.js";

const WATCHLIST_KEY = "md_watchlist_sellers";

// ============================================================
// MOCK FALLBACK — dev 단계에서 UI 확인용으로만 쓰는 목업 데이터.
// GET /api/evaluation/sellers 연동이 끝나면 이 배열 전체와, 이 배열을
// 참조하는 store/product.js의 mockProducts()를 함께 지우면 된다.
// 6개 이슈 규칙이 각각 최소 1건 이상 트리거되도록 설계되어 있다.
// ============================================================
export const MOCK_SELLERS = [
  {
    id: 1,
    name: "그린리빙",
    category: "생활용품",
    grade: "EXCELLENT",
    score: 92,
    joinedAt: "2024-03-12",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 540,
      categoryAvgSales30d: 380,
      sales7d: 130,
      salesPrev7d: 122,
      cancelRate: 3.8,
      refundRate: 2.1,
      revenue30d: 26400000,
      minRevenueThreshold: 3000000,
      daysSinceLastOrder: 0,
    },
    products: [
      { id: 101, name: "천연 소재 러그 매트", category: "생활용품", price: 39000, status: "ON_SALE", salesCount: 312 },
      { id: 102, name: "다용도 수납정리함 세트", category: "생활용품", price: 22000, status: "ON_SALE", salesCount: 228 },
    ],
    issues: [],
    review: {
      totalReviews: 214,
      negativeMentions: [{ tag: "배송 지연", count: 2, trend: "변동 없음" }],
      positiveMentions: [
        { tag: "빠른 배송", count: 58 },
        { tag: "꼼꼼한 포장", count: 41 },
      ],
      sampleQuote: "포장이 꼼꼼하고 배송도 빨라서 만족스러워요.",
    },
  },
  {
    id: 2,
    name: "프레시푸드",
    category: "식품",
    grade: "EXCELLENT",
    score: 88,
    joinedAt: "2023-11-02",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 610,
      categoryAvgSales30d: 420,
      sales7d: 150,
      salesPrev7d: 148,
      cancelRate: 4.5,
      refundRate: 3.4,
      revenue30d: 31200000,
      minRevenueThreshold: 4000000,
      daysSinceLastOrder: 0,
    },
    products: [
      { id: 201, name: "제철 과일 정기 박스", category: "식품", price: 32000, status: "ON_SALE", salesCount: 401 },
      { id: 202, name: "냉동 손만두 10팩", category: "식품", price: 18500, status: "ON_SALE", salesCount: 356 },
    ],
    issues: [],
    review: {
      totalReviews: 305,
      negativeMentions: [{ tag: "포장 파손", count: 4, trend: "+10%" }],
      positiveMentions: [{ tag: "신선도", count: 80 }],
      sampleQuote: "신선식품인데 포장도 신경써주셔서 좋았어요.",
    },
  },
  {
    id: 3,
    name: "데일리키친",
    category: "식품",
    grade: "EXCELLENT",
    score: 81,
    joinedAt: "2024-06-20",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 300,
      categoryAvgSales30d: 290,
      sales7d: 58,
      salesPrev7d: 92,
      cancelRate: 6.2,
      refundRate: 4.0,
      revenue30d: 12500000,
      minRevenueThreshold: 3000000,
      daysSinceLastOrder: 1,
    },
    products: [
      { id: 301, name: "실리콘 주방용품 6종 세트", category: "식품", price: 27000, status: "ON_SALE", salesCount: 189 },
      { id: 302, name: "논스틱 인덕션 프라이팬", category: "식품", price: 45000, status: "ON_SALE", salesCount: 111 },
    ],
    issues: [
      {
        type: "SALES_DECLINING",
        severity: 0.35,
        detail: "최근 7일 판매량이 이전 7일 대비 37% 감소 (58건 vs 92건)",
      },
    ],
    review: {
      totalReviews: 96,
      negativeMentions: [{ tag: "배송 지연", count: 6, trend: "+20%" }],
      positiveMentions: [{ tag: "맛", count: 30 }],
      sampleQuote: "맛은 좋은데 최근 배송이 조금 늦어졌어요.",
    },
  },
  {
    id: 4,
    name: "루미코스메틱",
    category: "뷰티",
    grade: "WARNING",
    score: 68,
    joinedAt: "2024-01-08",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 210,
      categoryAvgSales30d: 260,
      sales7d: 48,
      salesPrev7d: 55,
      cancelRate: 8.5,
      refundRate: 13.4,
      revenue30d: 9800000,
      minRevenueThreshold: 3000000,
      daysSinceLastOrder: 1,
    },
    products: [
      { id: 401, name: "수분 진정 크림 50ml", category: "뷰티", price: 28000, status: "ON_SALE", salesCount: 142 },
      { id: 402, name: "매트 립틴트 3종 세트", category: "뷰티", price: 21000, status: "HIDDEN", salesCount: 68 },
    ],
    issues: [
      {
        type: "HIGH_REFUND_RATE",
        severity: 0.55,
        detail: "환불율 13.4% (기준 10% 초과)",
      },
    ],
    review: {
      totalReviews: 152,
      negativeMentions: [
        { tag: "가품 의심", count: 11, trend: "최근 2주 3배 급증" },
        { tag: "변질/불량", count: 6, trend: "+50%" },
      ],
      positiveMentions: [{ tag: "향", count: 22 }],
      sampleQuote: "향은 좋은데 이거 정품 맞나요? 포장이 이상해요.",
    },
  },
  {
    id: 5,
    name: "테크가전마켓",
    category: "가전디지털",
    grade: "WARNING",
    score: 61,
    joinedAt: "2023-09-30",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 175,
      categoryAvgSales30d: 220,
      sales7d: 40,
      salesPrev7d: 46,
      cancelRate: 18.7,
      refundRate: 7.2,
      revenue30d: 41000000,
      minRevenueThreshold: 5000000,
      daysSinceLastOrder: 2,
    },
    products: [
      { id: 501, name: "무선 스틱 청소기", category: "가전디지털", price: 189000, status: "ON_SALE", salesCount: 96 },
      { id: 502, name: "블루투스 이어폰", category: "가전디지털", price: 59000, status: "ON_SALE", salesCount: 79 },
    ],
    issues: [
      {
        type: "HIGH_CANCEL_RATE",
        severity: 0.5,
        detail: "취소·반품율 18.7% (기준 15% 초과)",
      },
    ],
    review: {
      totalReviews: 88,
      negativeMentions: [
        { tag: "CS 불친절", count: 9, trend: "+40%" },
        { tag: "배송 지연", count: 5, trend: "+15%" },
      ],
      positiveMentions: [{ tag: "가격", count: 14 }],
      sampleQuote: "문의했는데 답변이 너무 늦고 퉁명스러웠어요.",
    },
  },
  {
    id: 6,
    name: "스포츠올데이",
    category: "스포츠",
    grade: "WARNING",
    score: 55,
    joinedAt: "2024-04-14",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 95,
      categoryAvgSales30d: 230,
      sales7d: 18,
      salesPrev7d: 30,
      cancelRate: 9.1,
      refundRate: 5.5,
      revenue30d: 6200000,
      minRevenueThreshold: 3000000,
      daysSinceLastOrder: 3,
    },
    products: [
      { id: 601, name: "프리미엄 요가매트", category: "스포츠", price: 34000, status: "ON_SALE", salesCount: 58 },
      { id: 602, name: "쿠셔닝 런닝화", category: "스포츠", price: 79000, status: "ON_SALE", salesCount: 37 },
    ],
    issues: [
      {
        type: "LOW_SALES",
        severity: 0.45,
        detail:
          "최근 30일 판매량이 카테고리 평균 대비 41% 수준 (95건 vs 평균 230건)",
      },
      {
        type: "SALES_DECLINING",
        severity: 0.4,
        detail: "최근 7일 판매량이 이전 7일 대비 40% 감소 (18건 vs 30건)",
      },
    ],
    review: {
      totalReviews: 41,
      negativeMentions: [{ tag: "사이즈 불일치", count: 5, trend: "+25%" }],
      positiveMentions: [{ tag: "품질", count: 9 }],
      sampleQuote: "사이즈가 설명과 다르게 와서 반품했어요.",
    },
  },
  {
    id: 7,
    name: "패션큐브",
    category: "패션",
    grade: "WARNING",
    score: 58,
    joinedAt: "2023-12-01",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 260,
      categoryAvgSales30d: 300,
      sales7d: 42,
      salesPrev7d: 78,
      cancelRate: 16.8,
      refundRate: 8.9,
      revenue30d: 15300000,
      minRevenueThreshold: 4000000,
      daysSinceLastOrder: 1,
    },
    products: [
      { id: 701, name: "오버사이즈 니트", category: "패션", price: 42000, status: "ON_SALE", salesCount: 121 },
      { id: 702, name: "와이드 데님 팬츠", category: "패션", price: 38000, status: "ON_SALE", salesCount: 94 },
    ],
    issues: [
      {
        type: "SALES_DECLINING",
        severity: 0.55,
        detail: "최근 7일 판매량이 이전 7일 대비 46% 감소 (42건 vs 78건)",
      },
      {
        type: "HIGH_CANCEL_RATE",
        severity: 0.35,
        detail: "취소·반품율 16.8% (기준 15% 초과)",
      },
    ],
    review: {
      totalReviews: 120,
      negativeMentions: [{ tag: "사이즈 불일치", count: 14, trend: "+30%" }],
      positiveMentions: [{ tag: "디자인", count: 33 }],
      sampleQuote: "디자인은 예쁜데 사이즈가 자주 안 맞아요.",
    },
  },
  {
    id: 8,
    name: "뷰티드림",
    category: "뷰티",
    grade: "WARNING",
    score: 72,
    joinedAt: "2024-07-02",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 190,
      categoryAvgSales30d: 260,
      sales7d: 40,
      salesPrev7d: 44,
      cancelRate: 7.0,
      refundRate: 6.1,
      revenue30d: 2600000,
      minRevenueThreshold: 3000000,
      daysSinceLastOrder: 2,
    },
    products: [
      { id: 801, name: "저자극 선크림 SPF50", category: "뷰티", price: 19000, status: "ON_SALE", salesCount: 88 },
      { id: 802, name: "약산성 클렌징 오일", category: "뷰티", price: 23000, status: "ON_SALE", salesCount: 61 },
    ],
    issues: [
      {
        type: "LOW_REVENUE",
        severity: 0.3,
        detail: "최근 30일 매출 260만원 (카테고리 최소 유지 기준 300만원 미달)",
      },
    ],
    review: {
      totalReviews: 64,
      negativeMentions: [{ tag: "배송 지연", count: 3, trend: "변동 없음" }],
      positiveMentions: [{ tag: "가성비", count: 19 }],
      sampleQuote: "가격 대비 괜찮은데 매출은 아직 적은 편인가봐요.",
    },
  },
  {
    id: 9,
    name: "빈티지클로젯",
    category: "패션",
    grade: "REVIEW",
    score: 38,
    joinedAt: "2023-05-19",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 130,
      categoryAvgSales30d: 300,
      sales7d: 20,
      salesPrev7d: 35,
      cancelRate: 23.4,
      refundRate: 16.8,
      revenue30d: 4100000,
      minRevenueThreshold: 4000000,
      daysSinceLastOrder: 4,
    },
    products: [
      { id: 901, name: "빈티지 플라워 원피스", category: "패션", price: 45000, status: "ON_SALE", salesCount: 43 },
      { id: 902, name: "체크 패턴 셔츠", category: "패션", price: 33000, status: "SOLD_OUT", salesCount: 51 },
    ],
    issues: [
      {
        type: "HIGH_CANCEL_RATE",
        severity: 0.85,
        detail: "취소·반품율 23.4% (기준 15% 초과, 심각)",
      },
      {
        type: "HIGH_REFUND_RATE",
        severity: 0.75,
        detail: "환불율 16.8% (기준 10% 초과, 심각)",
      },
      {
        type: "LOW_SALES",
        severity: 0.5,
        detail:
          "최근 30일 판매량이 카테고리 평균 대비 43% 수준 (130건 vs 평균 300건)",
      },
      {
        type: "SALES_DECLINING",
        severity: 0.45,
        detail: "최근 7일 판매량이 이전 7일 대비 43% 감소 (20건 vs 35건)",
      },
    ],
    review: {
      totalReviews: 77,
      negativeMentions: [
        { tag: "배송 지연", count: 18, trend: "최근 2주 3배 급증" },
        { tag: "CS 불친절", count: 10, trend: "+60%" },
        { tag: "오배송", count: 6, trend: "+80%" },
      ],
      positiveMentions: [{ tag: "디자인", count: 8 }],
      sampleQuote:
        "주문한 색상과 다른 제품이 왔고, 반품 문의에도 3일째 답이 없어요.",
    },
  },
  {
    id: 10,
    name: "디지털허브",
    category: "가전디지털",
    grade: "REVIEW",
    score: 45,
    joinedAt: "2023-08-11",
    sellerStatus: "ACTIVE",
    metrics: {
      sales30d: 88,
      categoryAvgSales30d: 220,
      sales7d: 12,
      salesPrev7d: 20,
      cancelRate: 12.0,
      refundRate: 21.3,
      revenue30d: 8900000,
      minRevenueThreshold: 5000000,
      daysSinceLastOrder: 16,
    },
    products: [
      { id: 1001, name: "스마트워치 GT3", category: "가전디지털", price: 129000, status: "ON_SALE", salesCount: 34 },
      { id: 1002, name: "보조배터리 20000mAh", category: "가전디지털", price: 29000, status: "HIDDEN", salesCount: 22 },
    ],
    issues: [
      {
        type: "HIGH_REFUND_RATE",
        severity: 0.9,
        detail: "환불율 21.3% (기준 10% 초과, 심각)",
      },
      {
        type: "NO_RECENT_ORDER",
        severity: 0.6,
        detail: "최근 16일간 신규 주문 없음 (기준 14일 초과)",
      },
      {
        type: "LOW_SALES",
        severity: 0.45,
        detail:
          "최근 30일 판매량이 카테고리 평균 대비 40% 수준 (88건 vs 평균 220건)",
      },
      {
        type: "SALES_DECLINING",
        severity: 0.4,
        detail: "최근 7일 판매량이 이전 7일 대비 40% 감소 (12건 vs 20건)",
      },
    ],
    review: {
      totalReviews: 53,
      negativeMentions: [
        { tag: "가품 의심", count: 7, trend: "최근 2주 2.5배 급증" },
        { tag: "AS 지연", count: 9, trend: "+35%" },
      ],
      positiveMentions: [{ tag: "가격", count: 6 }],
      sampleQuote:
        "정품 인증서가 없어서 가품이 아닌지 걱정돼요. AS 요청도 답이 없습니다.",
    },
  },
  {
    id: 11,
    name: "홈스타일마켓",
    category: "생활용품",
    grade: "REVIEW",
    score: 29,
    joinedAt: "2023-02-25",
    sellerStatus: "WARNING",
    metrics: {
      sales30d: 42,
      categoryAvgSales30d: 260,
      sales7d: 3,
      salesPrev7d: 9,
      cancelRate: 11.0,
      refundRate: 8.0,
      revenue30d: 980000,
      minRevenueThreshold: 3000000,
      daysSinceLastOrder: 19,
    },
    products: [
      { id: 1101, name: "북유럽 스타일 쿠션 커버", category: "생활용품", price: 15000, status: "SOLD_OUT", salesCount: 18 },
      { id: 1102, name: "감성 LED 무드등", category: "생활용품", price: 24000, status: "SOLD_OUT", salesCount: 12 },
    ],
    issues: [
      {
        type: "NO_RECENT_ORDER",
        severity: 0.7,
        detail: "최근 19일간 신규 주문 없음 (기준 14일 초과)",
      },
      {
        type: "LOW_REVENUE",
        severity: 0.67,
        detail:
          "최근 30일 매출 98만원 (카테고리 최소 유지 기준 300만원 대비 크게 미달)",
      },
      {
        type: "LOW_SALES",
        severity: 0.68,
        detail:
          "최근 30일 판매량이 카테고리 평균 대비 16% 수준 (42건 vs 평균 260건)",
      },
      {
        type: "SALES_DECLINING",
        severity: 0.55,
        detail: "최근 7일 판매량이 이전 7일 대비 67% 감소 (3건 vs 9건)",
      },
    ],
    review: {
      totalReviews: 12,
      negativeMentions: [{ tag: "응답 없음", count: 8, trend: "지속" }],
      positiveMentions: [],
      sampleQuote:
        "문의를 남겼는데 셀러가 아예 응답이 없어요. 운영을 안 하는 것 같아요.",
    },
  },
  {
    id: 12,
    name: "올가닉키즈",
    category: "생활용품",
    grade: "INSUFFICIENT",
    score: null,
    joinedAt: "2026-08-29",
    sellerStatus: "ACTIVE",
    insufficientNote:
      "신규 입점 5일 차로 평가에 필요한 최소 데이터가 누적되지 않아 등급 산정을 보류합니다. (안정화까지 약 25일 소요 예정)",
    metrics: {
      sales30d: 6,
      categoryAvgSales30d: 260,
      sales7d: 4,
      salesPrev7d: 2,
      cancelRate: 0,
      refundRate: 0,
      revenue30d: 180000,
      minRevenueThreshold: 3000000,
      daysSinceLastOrder: 0,
    },
    products: [
      { id: 1201, name: "유기농 이유식 5팩 세트", category: "생활용품", price: 26000, status: "ON_SALE", salesCount: 4 },
      { id: 1202, name: "아기 실리콘 식기 세트", category: "생활용품", price: 18000, status: "ON_SALE", salesCount: 2 },
    ],
    issues: [],
    review: {
      totalReviews: 2,
      negativeMentions: [],
      positiveMentions: [{ tag: "포장", count: 2 }],
      sampleQuote: "아직 후기가 많지 않아요.",
    },
  },
];
// ↑↑↑ MOCK FALLBACK 끝 (MOCK_SELLERS)

function loadWatchlist() {
  try {
    const raw = JSON.parse(localStorage.getItem(WATCHLIST_KEY) || "[]");
    return Array.isArray(raw) ? raw : [];
  } catch {
    return [];
  }
}

// seller-evaluation-service(recommend-service)는 등급을 한글 문자열로,
// 이슈 근거를 evidence 필드로 내려준다. 내부 화면 모델(GRADE_META 코드,
// issue.detail)로 정규화한다.
const GRADE_LABEL_TO_CODE = {
  우수: "EXCELLENT",
  주의: "WARNING",
  퇴출검토: "REVIEW",
  평가보류: "INSUFFICIENT"
};

function normalizeGrade(grade) {
  if (!grade) return "INSUFFICIENT";
  return GRADE_LABEL_TO_CODE[grade] || grade;
}

function normalizeIssue(issue) {
  return {
    type: issue.type,
    severity: issue.severity,
    detail: issue.evidence ?? issue.detail ?? ""
  };
}

// 실제 API 응답은 sellerId/sellerName/grade/score/issues 정도만 내려주고
// (metrics·review·products는 아직 없음) 화면은 이 필드가 없어도 깨지지
// 않도록 각 뷰에서 v-if로 방어한다.
function normalizeSeller(raw) {
  return {
    id: raw.sellerId ?? raw.id,
    name: raw.sellerName ?? raw.name,
    category: raw.category ?? null,
    grade: normalizeGrade(raw.grade),
    score: raw.score ?? null,
    joinedAt: raw.joinedAt ?? null,
    sellerStatus: raw.sellerStatus ?? "ACTIVE",
    insufficientNote: raw.insufficientNote ?? null,
    metrics: raw.metrics ?? null,
    issues: Array.isArray(raw.issues) ? raw.issues.map(normalizeIssue) : [],
    review: raw.review ?? null
  };
}

export const useEvaluationStore = defineStore("evaluation", () => {
  const sellers = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const watchlist = ref(loadWatchlist());

  function persistWatchlist() {
    localStorage.setItem(WATCHLIST_KEY, JSON.stringify(watchlist.value));
  }

  function isWatched(sellerId) {
    return watchlist.value.includes(Number(sellerId));
  }

  function toggleWatch(sellerId) {
    const id = Number(sellerId);
    watchlist.value = isWatched(id)
      ? watchlist.value.filter((v) => v !== id)
      : [...watchlist.value, id];
    persistWatchlist();
  }

  async function fetchSellers() {
    loading.value = true;
    error.value = null;

    try {
      const res = await evaluationApi.getSellers();
      console.log("[EvaluationStore] getSellers response =", res.data);

      // seller-evaluation-service 응답: { generatedAt, sellers: [...] }
      const raw = Array.isArray(res.data?.sellers)
        ? res.data.sellers
        : Array.isArray(res.data?.data)
          ? res.data.data
          : Array.isArray(res.data)
            ? res.data
            : [];

      if (raw.length) {
        sellers.value = raw.map(normalizeSeller);
      } else {
        throw new Error("empty response");
      }
    } catch (e) {
      // ↓↓↓ MOCK FALLBACK — /api/evaluation/sellers 연동 완료되면 이 catch 블록과
      // 파일 상단의 MOCK_SELLERS를 통째로 지우면 된다.
      console.warn(
        "[EvaluationStore] API 미연동 또는 실패 - 목업 데이터로 대체합니다:",
        e.message,
      );
      sellers.value = MOCK_SELLERS;
      // ↑↑↑ MOCK FALLBACK 끝
    } finally {
      loading.value = false;
    }
  }

  function getSellerById(id) {
    return sellers.value.find((s) => String(s.id) === String(id)) || null;
  }

  async function updateSellerStatus(sellerId, status) {
    try {
      await evaluationApi.updateSellerStatus(sellerId, status);
    } catch (e) {
      console.warn(
        "[EvaluationStore] 상태 확정 API 미연동(Sprint2) - 화면에만 반영합니다:",
        e.message,
      );
    } finally {
      const target = getSellerById(sellerId);
      if (target) target.sellerStatus = status;
    }
  }

  const gradeCounts = computed(() => {
    const counts = { EXCELLENT: 0, WARNING: 0, REVIEW: 0, INSUFFICIENT: 0 };
    sellers.value.forEach((s) => {
      if (counts[s.grade] !== undefined) counts[s.grade] += 1;
    });
    return counts;
  });

  // MD가 오늘 확인해야 할 순서대로 정렬 (퇴출검토 > 주의 > 평가보류, 그 안에서는 점수 낮은 순)
  const priorityQueue = computed(() => {
    const rank = { REVIEW: 0, WARNING: 1, INSUFFICIENT: 2, EXCELLENT: 3 };
    return [...sellers.value]
      .filter((s) => s.grade !== "EXCELLENT")
      .sort((a, b) => {
        if (rank[a.grade] !== rank[b.grade])
          return rank[a.grade] - rank[b.grade];
        return (a.score ?? 0) - (b.score ?? 0);
      });
  });

  return {
    sellers,
    loading,
    error,
    watchlist,
    isWatched,
    toggleWatch,
    fetchSellers,
    getSellerById,
    updateSellerStatus,
    gradeCounts,
    priorityQueue,
  };
});
