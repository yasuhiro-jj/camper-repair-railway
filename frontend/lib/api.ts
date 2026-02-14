import axios, { AxiosError } from 'axios';

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
  answer?: string; // UI互換（将来拡張）
  response?: string; // バックエンドの主キー
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

  // バックエンドのキー → フロントが参照するキーへ寄せる
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
      // /api/partner-shops は { shops, count } 形式
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
      // バックエンドは { success, deal, message } を返す
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
  async diagnose(payload: { message: string; category?: string; session_id?: string }): Promise<DiagnosticResponse> {
    try {
      // unified_chat の diagnostic モードを明示（UI側が mode を付けていないため）
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
      const res = await nextApi.post('/api/start-conversation', sessionId ? { session_id: sessionId } : {});
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

/**
 * APIクライアント
 * 既存のFlaskバックエンドAPIと通信するための関数群
 */

import axios from 'axios';
import { FactoryCase } from '@/types';

// バックエンドAPIのベースURL
// 開発環境: env があればそれを使い、なければローカル
// 本番環境(Vercel): 常にRailwayのURLを使用（localhost には飛ばさない）
const API_URL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002'
    : process.env.NEXT_PUBLIC_API_URL || 'https://web-production-c8b78.up.railway.app';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60秒のタイムアウト
});

// チャットAPI
export interface ChatMessage {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  answer?: string;
  response?: string;
  type?: string;
  error?: string;
}

export const chatApi = {
  /**
   * チャットメッセージを送信
   * クライアントからはNext.jsのAPIルート(`/api/chat`)を経由してバックエンドに接続する
   */
  sendMessage: async (
    message: string,
    sessionId?: string,
  ): Promise<ChatResponse> => {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!res.ok) {
      throw new Error(`チャットAPIエラー: ${res.status}`);
    }

    const data = (await res.json()) as ChatResponse;
    return data;
  },

  /**
   * 会話を開始
   * クライアントからはNext.jsのAPIルート(`/api/start-conversation`)を経由してバックエンドに接続する
   */
  startConversation: async (sessionId?: string): Promise<ChatResponse> => {
    const res = await fetch("/api/start-conversation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });

    if (!res.ok) {
      throw new Error(`会話開始APIエラー: ${res.status}`);
    }

    const data = (await res.json()) as ChatResponse;
    return data;
  },
};

// 工場ダッシュボードAPI
export const factoryApi = {
  /**
   * 案件一覧を取得
   * @param status ステータスフィルタ（オプション）
   * @param partnerPageId パートナー工場のNotion Page ID（指定された場合、その工場に紹介された案件のみ取得）
   */
  getCases: async (status?: string, partnerPageId?: string): Promise<FactoryCase[]> => {
    try {
      const params: Record<string, string> = {};
      if (status) params.status = status;
      if (partnerPageId) params.partner_page_id = partnerPageId;
      
      const response = await apiClient.get<{ success: boolean; cases: FactoryCase[] }>('/admin/api/cases', { params });
      
      if (response.data.success && response.data.cases) {
        return response.data.cases;
      }
      
      // 互換性のため、casesが直接配列の場合も対応
      if (Array.isArray(response.data)) {
        return response.data;
      }
      
      return [];
    } catch (error: any) {
      console.error('案件取得APIエラー:', error);
      if (error.response) {
        console.error('レスポンス:', error.response.data);
        console.error('ステータス:', error.response.status);
      }
      throw error;
    }
  },

  /**
   * 案件のステータスを更新
   */
  updateCaseStatus: async (pageId: string, status: string): Promise<void> => {
    await apiClient.post('/admin/api/update-status', {
      page_id: pageId,
      status,
    });
  },

  /**
   * コメントを追加
   */
  addComment: async (pageId: string, comment: string): Promise<void> => {
    await apiClient.post('/admin/api/add-comment', {
      page_id: pageId,
      comment,
    });
  },
};

// 作業マニュアルDB API
export interface Manual {
  id: string;
  manual_id?: string;
  title?: string;
  category?: string;
  difficulty?: string;
  steps?: string;
  parts?: string;
  time_estimate?: string;
  [key: string]: any;
}

export const manualApi = {
  /**
   * 作業マニュアルを検索
   * @param query 検索クエリ
   * @param category カテゴリフィルタ（オプション）
   * @param difficulty 難易度フィルタ（オプション）
   * @param limit 最大取得件数（デフォルト: 10）
   */
  searchManuals: async (
    query: string,
    category?: string,
    difficulty?: string,
    limit: number = 10
  ): Promise<{ manuals: Manual[]; count: number }> => {
    try {
      const response = await apiClient.post<{
        manuals: Manual[];
        count: number;
        query: string;
        filters: { category?: string; difficulty?: string };
      }>('/api/factory/manual/search', {
        query,
        category: category || '',
        difficulty: difficulty || '',
        limit,
      });

      return {
        manuals: response.data.manuals || [],
        count: response.data.count || 0,
      };
    } catch (error: any) {
      console.error('作業マニュアル検索APIエラー:', error);
      if (error.response) {
        console.error('レスポンス:', error.response.data);
        console.error('ステータス:', error.response.status);
      }
      throw error;
    }
  },

  /**
   * マニュアル詳細を取得
   * @param manualId マニュアルID
   */
  getManualDetail: async (manualId: string): Promise<Manual> => {
    try {
      const response = await apiClient.get<Manual>(`/api/factory/manual/${manualId}`);
      return response.data;
    } catch (error: any) {
      console.error('マニュアル詳細取得APIエラー:', error);
      throw error;
    }
  },
};

// 工場マッチングAPI（フェーズ4-1）
export interface CaseInfo {
  category?: string;
  user_message?: string;
  customer_location?: string;
  prefecture?: string;
}

export interface MatchedFactory {
  factory_id: string;
  name: string;
  prefecture: string;
  specialties: string[];
  matching_score: number;
  score_details: {
    location_score: number;
    specialty_score: number;
    workload_score: number;
    rating_score: number;
    total_score: number;
  };
  [key: string]: any;
}

export const factoryMatchingApi = {
  /**
   * 案件に最適な工場をマッチング
   */
  matchFactories: async (
    caseInfo: CaseInfo,
    maxResults: number = 5
  ): Promise<MatchedFactory[]> => {
    try {
      const response = await apiClient.post<{
        success: boolean;
        matched_factories: MatchedFactory[];
        count: number;
      }>('/api/v1/factories/match', {
        case: caseInfo,
        max_results: maxResults,
      });

      if (response.data.success && response.data.matched_factories) {
        return response.data.matched_factories;
      }

      return [];
    } catch (error: any) {
      console.error('工場マッチングAPIエラー:', error);
      throw error;
    }
  },

  /**
   * 案件を自動的に最適な工場に割り当て
   */
  autoAssignCase: async (
    caseId: string,
    caseInfo: CaseInfo
  ): Promise<MatchedFactory | null> => {
    try {
      const response = await apiClient.post<{
        success: boolean;
        assigned_factory?: MatchedFactory;
        error?: string;
      }>(`/api/v1/cases/${caseId}/auto-assign`, {
        case: caseInfo,
      });

      if (response.data.success && response.data.assigned_factory) {
        return response.data.assigned_factory;
      }

      return null;
    } catch (error: any) {
      console.error('案件自動割り当てAPIエラー:', error);
      throw error;
    }
  },
};

// パートナー修理店API（フェーズ4-2）
export interface PartnerShop {
  shop_id: string;
  name: string;
  phone: string;
  email: string;
  prefecture: string;
  address: string;
  specialties: string[];
  business_hours: string;
  initial_diagnosis_fee: number;
  success_rate: number;
  total_referrals: number;
  total_deals: number;
  status: string;
  line_notification: boolean;
  line_webhook_url?: string;
  line_bot_id?: string;
  line_user_id?: string;
  page_id: string;
  // 評価関連
  avg_rating?: number;
  review_count?: number;
  repair_count?: number;
  total_repair_amount?: number;
  latest_review_date?: string;
  [key: string]: any;
}

export interface Deal {
  deal_id: string;
  customer_name: string;
  phone: string;
  email?: string;
  prefecture: string;
  symptom_category: string;
  symptom_detail: string;
  partner_page_ids: string[];
  inquiry_date: string;
  status: string;
  deal_date?: string;
  deal_amount: number;
  commission_rate: number;
  commission_amount: number;
  payment_status: string;
  notes?: string;
  page_id: string;
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
  notification_method?: 'email' | 'line'; // 通知方法: メール、LINE
  line_user_id?: string; // LINE通知を希望する場合のLINEユーザーID
}

// お客様からの備考追加API
export const customerNoteApi = {
  async addNote(
    dealId: string,
    note: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    const res = await fetch(`/api/customer-notes/${dealId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ note }),
    });

    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({}));
      throw new Error(errorBody.error || 'メッセージ送信APIでエラーが発生しました');
    }

    return res.json();
  },
};

export const partnerShopApi = {
  /**
   * パートナー修理店一覧を取得
   */
   getShops: async (
    status?: string,
    prefecture?: string,
    specialty?: string
  ): Promise<PartnerShop[]> => {
    try {
      // Next.jsのAPIルート経由でリクエスト（CORS問題を回避）
      const params = new URLSearchParams();
      if (status) params.append('status', status);
      if (prefecture) params.append('prefecture', prefecture);
      if (specialty) params.append('specialty', specialty);

      const queryString = params.toString();
      const url = `/api/partner-shops${queryString ? `?${queryString}` : ''}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.shops || [];
    } catch (error: any) {
      console.error('パートナー修理店一覧取得エラー:', error);
      throw new Error('パートナー修理店の取得に失敗しました: ' + error.message);
    }
  },

  /**
   * パートナー修理店詳細を取得
   */
  getShop: async (shopId: string): Promise<PartnerShop | null> => {
    try {
      const response = await apiClient.get<PartnerShop>(
        `/api/v1/partner-shops/${shopId}`
      );
      return response.data;
    } catch (error: any) {
      console.error('パートナー修理店取得エラー:', error);
      return null;
    }
  },
};

export const dealApi = {
  /**
   * 問い合わせフォームを送信（商談作成）
   */
  submitInquiry: async (formData: InquiryFormData): Promise<Deal> => {
    try {
      // Vercel上では同一オリジンのNext.js APIルート経由にしてCORS/Network Errorを回避
      const res = await fetch('/api/deals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = (await res.json()) as { success?: boolean; deal?: Deal; message?: string; error?: string };
      if (res.ok && data?.success && data?.deal) return data.deal;
      throw new Error(data?.message || data?.error || `問い合わせの送信に失敗しました (${res.status})`);
    } catch (error: any) {
      console.error('問い合わせ送信エラー:', error);
      throw error;
    }
  },

  /**
   * 商談一覧を取得
   */
  getDeals: async (
    status?: string,
    partnerPageId?: string
  ): Promise<Deal[]> => {
    try {
      const params: any = {};
      if (status) params.status = status;
      if (partnerPageId) params.partner_page_id = partnerPageId;

      const response = await apiClient.get<{
        deals: Deal[];
        count: number;
      }>('/api/v1/deals', { params });

      return response.data.deals || [];
    } catch (error: any) {
      console.error('商談一覧取得エラー:', error);
      throw error;
    }
  },

  /**
   * 商談ステータスを更新
   */
  updateStatus: async (
    dealId: string,
    status: string
  ): Promise<Deal> => {
    try {
      const response = await apiClient.patch<{
        success: boolean;
        deal: Deal;
      }>(`/api/v1/deals/${dealId}/status`, { status });

      if (response.data.success && response.data.deal) {
        return response.data.deal;
      }

      throw new Error('ステータス更新に失敗しました');
    } catch (error: any) {
      console.error('ステータス更新エラー:', error);
      throw error;
    }
  },

  /**
   * 成約金額を更新
   */
  updateAmount: async (
    dealId: string,
    dealAmount: number,
    commissionRate?: number
  ): Promise<Deal> => {
    try {
      const response = await apiClient.patch<{
        success: boolean;
        deal: Deal;
      }>(`/api/v1/deals/${dealId}/amount`, {
        deal_amount: dealAmount,
        commission_rate: commissionRate,
      });

      if (response.data.success && response.data.deal) {
        return response.data.deal;
      }

      throw new Error('成約金額更新に失敗しました');
    } catch (error: any) {
      console.error('成約金額更新エラー:', error);
      throw error;
    }
  },
};

// 管理者API
export interface FileInfo {
  name: string;
  size: string;
}

export interface SystemInfo {
  dbStatus: string;
  docCount: number;
}

export interface Builder {
  id: string;
  name: string;
  prefecture: string;
  address: string;
  phone: string;
  email: string;
  status: string;
}

export const adminApi = {
  /**
   * データベースを再構築
   */
  reloadDatabase: async (): Promise<{ success: boolean; message?: string; error?: string }> => {
    const response = await apiClient.post('/reload_data');
    return response.data;
  },

  /**
   * ファイル一覧を取得
   */
  getFileList: async (): Promise<FileInfo[]> => {
    try {
      const response = await apiClient.get('/api/admin/files');
      return response.data.files || [];
    } catch (error) {
      console.error('ファイル一覧取得エラー:', error);
      return [];
    }
  },

  /**
   * システム情報を取得
   */
  getSystemInfo: async (): Promise<SystemInfo> => {
    try {
      const response = await apiClient.get('/api/admin/system-info');
      return response.data;
    } catch (error) {
      console.error('システム情報取得エラー:', error);
      return {
        dbStatus: 'エラー',
        docCount: 0,
      };
    }
  },

  /**
   * ビルダー一覧を取得
   */
  getBuilders: async (): Promise<Builder[]> => {
    try {
      const response = await apiClient.get('/api/v1/builders');
      return response.data.builders || [];
    } catch (error) {
      console.error('ビルダー一覧取得エラー:', error);
      throw error;
    }
  },

  /**
   * 工場ネットワーク情報を取得
   */
  getFactoryNetwork: async () => {
    try {
      const response = await apiClient.get('/api/admin/factory-network');
      return response.data;
    } catch (error) {
      console.error('工場ネットワーク情報取得エラー:', error);
      return { factories: [] };
    }
  },

  /**
   * トラブル傾向分析を取得
   */
  getAnalytics: async () => {
    try {
      const response = await apiClient.get('/api/admin/analytics');
      return response.data;
    } catch (error) {
      console.error('トラブル傾向分析取得エラー:', error);
      return { trends: [] };
    }
  },
};

// 工賃推定API（フェーズ4-4）
export interface CostEstimationRequest {
  symptoms: string;
  category?: string;
  vehicle_info?: string;
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
  reasoning: string;
  similar_cases_count?: number;
  similar_cases_avg_cost?: number;
}

export const costEstimationApi = {
  /**
   * 工賃を推定
   */
  estimateCost: async (request: CostEstimationRequest): Promise<CostEstimation> => {
    try {
      const res = await fetch('/api/cost-estimation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      const data = (await res.json()) as { success?: boolean; estimation?: CostEstimation; error?: string };
      if (res.ok && data?.success && data?.estimation) return data.estimation;
      throw new Error(data?.error || `工賃推定に失敗しました (${res.status})`);
    } catch (error: any) {
      console.error('工賃推定APIエラー:', error);
      throw error;
    }
  },
};

// 診断API
export interface DiagnosticRequest {
  message: string;
  category?: string;
}

export interface DiagnosticResponse {
  response?: string;
  message?: string;
  diagnosis?: any;
  type?: string;
  rag_results?: any;
  notion_results?: any;
  error?: string;
}

export const diagnosticApi = {
  /**
   * 症状を診断
   */
  diagnose: async (request: DiagnosticRequest): Promise<DiagnosticResponse> => {
    try {
      const res = await fetch('/api/diagnostic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
        message: request.message,
        mode: 'diagnostic',
        include_serp: false,
        }),
      });

      const data = (await res.json()) as DiagnosticResponse;
      if (!res.ok) throw new Error(data?.error || `診断に失敗しました (${res.status})`);
      if (data?.error) throw new Error(data.error);
      return data;
    } catch (error: any) {
      console.error('診断APIエラー:', error);
      throw error;
    }
  },
};

// 評価API
export interface Review {
  review_id: string;
  deal_id: string;
  partner_page_id: string;
  customer_name: string;
  star_rating: number;
  comment: string;
  review_date: string;
  status: string;
  anonymous: boolean;
  [key: string]: any;
}

export interface CreateReviewRequest {
  deal_id: string;
  partner_page_id: string;
  customer_name: string;
  star_rating: number;
  comment?: string;
  anonymous?: boolean;
}

export const reviewApi = {
  /**
   * 評価を作成
   */
  createReview: async (
    dealId: string,
    partnerPageId: string,
    customerName: string,
    starRating: number,
    comment: string = '',
    anonymous: boolean = false
  ): Promise<Review> => {
    try {
      const response = await apiClient.post<{
        success: boolean;
        review: Review;
        error?: string;
      }>('/api/v1/reviews', {
        deal_id: dealId,
        partner_page_id: partnerPageId,
        customer_name: customerName,
        star_rating: starRating,
        comment: comment,
        anonymous: anonymous,
      });

      if (response.data.success && response.data.review) {
        return response.data.review;
      }

      throw new Error(response.data.error || '評価の作成に失敗しました');
    } catch (error: any) {
      console.error('評価作成APIエラー:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  /**
   * 評価一覧を取得
   */
  getReviews: async (
    partnerPageId?: string,
    status?: string,
    limit: number = 20
  ): Promise<Review[]> => {
    try {
      const params: any = {};
      if (partnerPageId) params.partner_page_id = partnerPageId;
      if (status) params.status = status;
      params.limit = limit;

      const response = await apiClient.get<{
        success: boolean;
        reviews: Review[];
        count: number;
      }>('/api/v1/reviews', { params });

      if (response.data.success && response.data.reviews) {
        return response.data.reviews;
      }

      return [];
    } catch (error: any) {
      console.error('評価一覧取得APIエラー:', error);
      throw error;
    }
  },
};

export default apiClient;
