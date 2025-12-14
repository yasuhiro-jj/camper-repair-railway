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
    : 'https://web-development-8c2f.up.railway.app';

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
    // 共通のAPIクライアント(apiClient)を利用してバックエンドにリクエストを送信
    const response = await apiClient.post(
      `/v1/deals/${dealId}/customer-notes`,
      { note }
    );
    return response.data;
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
      const response = await apiClient.post<{
        success: boolean;
        deal: Deal;
        message: string;
      }>('/api/v1/deals', formData);

      if (response.data.success && response.data.deal) {
        return response.data.deal;
      }

      throw new Error(response.data.message || '問い合わせの送信に失敗しました');
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
      const response = await apiClient.post<{
        success: boolean;
        estimation: CostEstimation;
        error?: string;
      }>('/api/v1/cost-estimation', request);

      if (response.data.success && response.data.estimation) {
        return response.data.estimation;
      }

      throw new Error(response.data.error || '工賃推定に失敗しました');
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
  response: string;
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
      const response = await apiClient.post<DiagnosticResponse>('/api/unified/chat', {
        message: request.message,
        mode: 'diagnostic',
        include_serp: false,
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      return response.data;
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


これであっているのですよね。　Commit changesする？必要ある？
