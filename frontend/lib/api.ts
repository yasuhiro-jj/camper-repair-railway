import axios from 'axios';

/**
 * フロントエンド用 API ラッパ
 *
 * - `@/lib/api` として各ページ/コンポーネントから参照される想定
 * - Next.js の `/app/api/*`（プロキシ）経由のものと、バックエンド直叩きのものを混在
 */

const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002';

// バックエンド直叩き用（CORSが許可されている前提）
const backendApi = axios.create({
  baseURL: BACKEND_BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

// Next.js API ルート（同一オリジン）用
const nextApi = axios.create({
  baseURL: '',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

function toMessage(err: unknown, fallback: string) {
  if (axios.isAxiosError(err)) {
    const data: any = err.response?.data;
    return (
      data?.error ||
      data?.message ||
      (typeof data === 'string' ? data : null) ||
      err.message ||
      fallback
    );
  }
  if (err instanceof Error) return err.message || fallback;
  return fallback;
}

// ========= 型定義 =========

export interface Manual {
  id?: string;
  manual_id?: string;
  title?: string;
  category?: string;
  difficulty?: string;
  steps?: string;
  parts?: string;
  time_estimate?: string;
  url?: string;
  [key: string]: any;
}

export interface CaseInfo {
  category: string;
  user_message: string;
  customer_location: string;
  // 画面側が `prefecture` を渡すケースもあるため互換で持つ
  prefecture?: string;
  [key: string]: any;
}

export interface MatchedFactory {
  factory_id?: string;
  name?: string;
  prefecture?: string;
  specialties?: string[];
  matching_score: number; // 0-1
  score_details?: {
    // フロント実装が参照しているキー（互換）
    location_score?: number;
    specialty_score?: number;
    workload_score?: number;
    rating_score?: number;
    // バックエンドが返す可能性のあるキーも保持
    category_match?: number;
    location_match?: number;
    capacity_match?: number;
    [key: string]: any;
  };
  [key: string]: any;
}

export interface InquiryFormData {
  customer_name: string;
  phone: string;
  email?: string;
  prefecture: string;
  symptom_category: string;
  symptom_detail: string;
  partner_page_id: string;
  notification_method: 'email' | 'line';
  line_user_id?: string;
}

export interface CostEstimation {
  estimated_work_hours: number;
  difficulty: string;
  labor_cost_min: number;
  labor_cost_max: number;
  parts_cost_min: number;
  parts_cost_max: number;
  diagnosis_fee: number;
  total_cost_min: number;
  total_cost_max: number;
  reasoning?: string;
  similar_cases_count?: number;
  [key: string]: any;
}

export interface PartnerShop {
  shop_id?: string;
  page_id?: string;
  name?: string;
  prefecture?: string;
  address?: string;
  phone?: string;
  email?: string;
  specialties?: string[];
  status?: string;
  // LINE関連（UIで参照）
  line_bot_id?: string;
  line_webhook_url?: string;
  line_user_id?: string;
  line_notification?: boolean;
  [key: string]: any;
}

export interface DiagnosticResponse {
  response?: string;
  answer?: string;
  message?: string;
  error?: string;
  notion_results?: any;
  rag_results?: any;
  serp_results?: any;
  diagnosis?: any;
  [key: string]: any;
}

export interface ChatResponse {
  answer?: string;
  response?: string;
  error?: string;
  timeout?: boolean;
  elapsed_time?: string;
  rag_results?: any;
  notion_results?: any;
  serp_results?: any;
  [key: string]: any;
}

// ========= API ラッパ =========

export const authApi = {
  async login(loginId: string, password: string): Promise<any> {
    try {
      const res = await backendApi.post('/api/v1/auth/login', {
        login_id: loginId,
        password,
      });
      return res.data;
    } catch (err) {
      throw new Error(toMessage(err, 'ログインに失敗しました'));
    }
  },

  async requestPasswordReset(email: string): Promise<any> {
    try {
      const res = await backendApi.post('/api/v1/auth/request-password-reset', { email });
      return res.data;
    } catch (err) {
      throw new Error(toMessage(err, 'パスワードリセットメールの送信に失敗しました'));
    }
  },

  async resetPassword(token: string, newPassword: string): Promise<any> {
    try {
      const res = await backendApi.post('/api/v1/auth/reset-password', {
        token,
        new_password: newPassword,
      });
      return res.data;
    } catch (err) {
      throw new Error(toMessage(err, 'パスワードのリセットに失敗しました'));
    }
  },
};

export const factoryApi = {
  async getCases(status?: string, partnerPageId?: string): Promise<any[]> {
    try {
      const res = await backendApi.get('/admin/api/cases', {
        params: {
          status: status || undefined,
          partner_page_id: partnerPageId || undefined,
          limit: 100,
        },
      });
      const data = res.data as any;
      if (data?.success === false) {
        throw new Error(data?.error || '案件の取得に失敗しました');
      }
      return data?.cases || [];
    } catch (err) {
      throw new Error(toMessage(err, '案件の取得に失敗しました'));
    }
  },

  async updateCaseStatus(pageId: string, status: string): Promise<void> {
    try {
      const res = await backendApi.post('/admin/api/update-status', {
        page_id: pageId,
        status,
      });
      const data = res.data as any;
      if (data?.success === false) {
        throw new Error(data?.error || 'ステータス更新に失敗しました');
      }
    } catch (err) {
      throw new Error(toMessage(err, 'ステータス更新に失敗しました'));
    }
  },

  async addComment(pageId: string, comment: string): Promise<void> {
    try {
      const res = await backendApi.post('/admin/api/add-comment', {
        page_id: pageId,
        comment,
      });
      const data = res.data as any;
      if (data?.success === false) {
        throw new Error(data?.error || 'コメント追加に失敗しました');
      }
    } catch (err) {
      throw new Error(toMessage(err, 'コメント追加に失敗しました'));
    }
  },
};

export const manualApi = {
  async searchManuals(
    query: string,
    category?: string,
    difficulty?: string,
    limit: number = 10,
  ): Promise<{ manuals: Manual[]; count: number }> {
    try {
      const res = await backendApi.post('/api/factory/manual/search', {
        query,
        category: category || '',
        difficulty: difficulty || '',
        limit,
      });
      return res.data as any;
    } catch (err) {
      throw new Error(toMessage(err, 'マニュアルの検索に失敗しました'));
    }
  },

  async getManualDetail(manualId: string): Promise<Manual> {
    try {
      const res = await backendApi.get(`/api/factory/manual/${encodeURIComponent(manualId)}`);
      return res.data as any;
    } catch (err) {
      throw new Error(toMessage(err, 'マニュアルの取得に失敗しました'));
    }
  },
};

function normalizeScoreDetails(scoreDetails: any): MatchedFactory['score_details'] | undefined {
  if (!scoreDetails || typeof scoreDetails !== 'object') return undefined;

  const categoryMatch =
    typeof scoreDetails.category_match === 'number' ? scoreDetails.category_match : undefined;
  const locationMatch =
    typeof scoreDetails.location_match === 'number' ? scoreDetails.location_match : undefined;
  const capacityMatch =
    typeof scoreDetails.capacity_match === 'number' ? scoreDetails.capacity_match : undefined;
  const ratingScore =
    typeof scoreDetails.rating_score === 'number' ? scoreDetails.rating_score : undefined;

  return {
    ...scoreDetails,
    specialty_score:
      typeof scoreDetails.specialty_score === 'number'
        ? scoreDetails.specialty_score
        : categoryMatch,
    location_score:
      typeof scoreDetails.location_score === 'number'
        ? scoreDetails.location_score
        : locationMatch,
    workload_score:
      typeof scoreDetails.workload_score === 'number'
        ? scoreDetails.workload_score
        : capacityMatch,
    rating_score: ratingScore,
  };
}

export const factoryMatchingApi = {
  async matchFactories(caseInfo: CaseInfo, maxResults: number = 5): Promise<MatchedFactory[]> {
    try {
      const res = await backendApi.post('/api/v1/factories/match', {
        case: caseInfo,
        max_results: maxResults,
      });
      const data = res.data as any;
      if (data?.success === false) {
        throw new Error(data?.error || 'マッチングに失敗しました');
      }
      const factories: any[] = data?.matched_factories || [];
      return factories.map((f) => ({
        ...f,
        matching_score: typeof f?.matching_score === 'number' ? f.matching_score : 0,
        score_details: normalizeScoreDetails(f?.score_details),
      })) as MatchedFactory[];
    } catch (err) {
      throw new Error(toMessage(err, 'マッチングに失敗しました'));
    }
  },

  async autoAssignCase(caseId: string, caseInfo: CaseInfo): Promise<MatchedFactory | null> {
    try {
      const res = await backendApi.post(`/api/v1/cases/${encodeURIComponent(caseId)}/auto-assign`, {
        case: caseInfo,
      });
      const data = res.data as any;
      if (data?.success === false) {
        throw new Error(data?.error || '自動割り当てに失敗しました');
      }
      const assigned = data?.assigned_factory;
      if (!assigned) return null;
      return {
        ...assigned,
        matching_score: typeof assigned?.matching_score === 'number' ? assigned.matching_score : 0,
        score_details: normalizeScoreDetails(assigned?.score_details),
      } as MatchedFactory;
    } catch (err) {
      throw new Error(toMessage(err, '自動割り当てに失敗しました'));
    }
  },
};

export const partnerShopApi = {
  async getShops(
    status?: string,
    prefecture?: string,
    specialty?: string,
  ): Promise<PartnerShop[]> {
    try {
      const res = await nextApi.get('/api/partner-shops', {
        params: {
          status: status || undefined,
          prefecture: prefecture || undefined,
          specialty: specialty || undefined,
        },
      });
      const data = res.data as any;
      return (data?.shops || []) as PartnerShop[];
    } catch (err) {
      throw new Error(toMessage(err, 'パートナー修理店の取得に失敗しました'));
    }
  },
};

export const dealApi = {
  async submitInquiry(formData: InquiryFormData): Promise<{ deal_id: string; [k: string]: any }> {
    try {
      const res = await nextApi.post('/api/deals', formData);
      const data = res.data as any;
      if (data?.success === false) {
        throw new Error(data?.error || '問い合わせの送信に失敗しました');
      }
      return (data?.deal || data) as any;
    } catch (err) {
      throw new Error(toMessage(err, '問い合わせの送信に失敗しました'));
    }
  },
};

export const customerNoteApi = {
  async addNote(dealId: string, note: string): Promise<{ success: boolean; error?: string }> {
    try {
      const res = await nextApi.post(`/api/customer-notes/${encodeURIComponent(dealId)}`, {
        note,
      });
      return res.data as any;
    } catch (err) {
      throw new Error(toMessage(err, 'メッセージの送信に失敗しました'));
    }
  },
};

export const costEstimationApi = {
  async estimateCost(payload: {
    symptoms: string;
    category?: string;
    vehicle_info?: string;
  }): Promise<CostEstimation> {
    try {
      const res = await nextApi.post('/api/cost-estimation', payload);
      const data = res.data as any;
      if (data?.success === false) {
        throw new Error(data?.error || '工賃推定に失敗しました');
      }
      return (data?.estimation || data) as CostEstimation;
    } catch (err) {
      throw new Error(toMessage(err, '工賃推定に失敗しました'));
    }
  },
};

export const diagnosticApi = {
  async diagnose(payload: {
    message: string;
    category?: string;
    session_id?: string;
  }): Promise<DiagnosticResponse> {
    try {
      const res = await nextApi.post('/api/diagnostic', {
        ...payload,
        mode: 'diagnostic',
      });
      return res.data as any;
    } catch (err) {
      throw new Error(toMessage(err, '診断に失敗しました'));
    }
  },
};

export const chatApi = {
  async startConversation(sessionId?: string): Promise<{ conversation_id: string }> {
    try {
      const res = await nextApi.post(
        '/api/start-conversation',
        sessionId ? { session_id: sessionId } : {},
      );
      return res.data as any;
    } catch (err) {
      throw new Error(toMessage(err, '会話開始に失敗しました'));
    }
  },

  async sendMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    try {
      const res = await nextApi.post('/api/chat', {
        message,
        session_id: sessionId,
        mode: 'chat',
        include_serp: true,
      });
      return res.data as any;
    } catch (err) {
      throw new Error(toMessage(err, 'メッセージの送信に失敗しました'));
    }
  },
};

export const reviewApi = {
  async createReview(
    dealId: string,
    partnerPageId: string,
    customerName: string,
    starRating: number,
    comment: string,
    anonymous: boolean,
  ): Promise<any> {
    try {
      const res = await backendApi.post('/api/v1/reviews', {
        deal_id: dealId,
        partner_page_id: partnerPageId,
        customer_name: customerName,
        star_rating: starRating,
        comment,
        anonymous,
      });
      const data = res.data as any;
      if (data?.success === false) {
        throw new Error(data?.error || '評価の送信に失敗しました');
      }
      return data;
    } catch (err) {
      throw new Error(toMessage(err, '評価の送信に失敗しました'));
    }
  },
};

export const adminApi = {
  async getSystemInfo(): Promise<{ dbStatus: string; docCount: number }> {
    try {
      const res = await backendApi.get('/api/admin/system-info');
      return res.data as any;
    } catch (err) {
      throw new Error(toMessage(err, 'システム情報の取得に失敗しました'));
    }
  },

  async reloadDatabase(): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const res = await backendApi.post('/reload_data', {});
      return res.data as any;
    } catch (err) {
      throw new Error(toMessage(err, 'データベースの再構築に失敗しました'));
    }
  },

  async getBuilders(): Promise<any[]> {
    try {
      const res = await backendApi.get('/api/v1/builders', { params: { limit: 100 } });
      const data = res.data as any;
      return data?.builders || [];
    } catch (err) {
      throw new Error(toMessage(err, 'ビルダー一覧の取得に失敗しました'));
    }
  },
};

