/**
 * TypeScript型定義
 */

// チャット関連
export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai' | 'system';
  timestamp: Date;
}

export interface ChatSession {
  id: string;
  messages: Message[];
  createdAt: Date;
}

// 工場ダッシュボード関連
export interface FactoryCase {
  id: string;
  page_id?: string; // 既存APIとの互換性
  title: string;
  status: string; // '受付' | '診断中' | '修理中' | '完了' | 'キャンセル' または 'pending' | 'in_progress' | 'completed' | 'cancelled'
  customerName?: string;
  description?: string;
  user_message?: string;
  bot_message?: string;
  category?: string;
  session_id?: string;
  timestamp?: string;
  created_time?: string;
  createdAt: string;
  updatedAt: string;
  comments?: string[];
  comment?: string;
  [key: string]: any; // その他のプロパティに対応
}

// 管理者画面関連
export interface Factory {
  id: string;
  name: string;
  location: string;
  specialties: string[];
  status: 'active' | 'inactive';
}

export interface Analytics {
  totalCases: number;
  completedCases: number;
  pendingCases: number;
  averageCompletionTime: number;
  topIssues: Array<{
    category: string;
    count: number;
  }>;
}

