'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { FactoryCase } from '@/types';
import { factoryApi } from '@/lib/api';
import { useAuthGuard } from '@/lib/authGuard';
import CaseList from '@/components/Factory/CaseList';
import StatusFilter from '@/components/Factory/StatusFilter';
import FactoryMatching from '@/components/Factory/FactoryMatching';
import ManualSearchModal from '@/components/Factory/ManualSearchModal';
import Navigation from '@/components/Navigation';

function FactoryDashboardPageContent() {
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: isAuthLoading } = useAuthGuard();
  const [cases, setCases] = useState<FactoryCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeStatus, setActiveStatus] = useState<string>('');
  const [isManualSearchOpen, setIsManualSearchOpen] = useState(false);
  const [userRole, setUserRole] = useState<string | null>(null);
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setUserRole(localStorage.getItem('role'));
    }
  }, [isAuthenticated]);
  
  // 案件取得時の工場ID（各工場は自社の案件のみ、管理者は全件）
  const getPartnerPageIdForApi = (): string | undefined => {
    if (typeof window === 'undefined') return undefined;
    
    const role = localStorage.getItem('role');
    const factoryId = localStorage.getItem('factory_id');
    
    // 工場ロール: 必ず自社のfactory_idでフィルタ（他社の案件は見せない）
    if (role === 'factory' && factoryId) {
      return factoryId;
    }
    
    // 管理者ロール: URLで指定があればその工場のみ、なければ全件
    if (role === 'admin') {
      const urlPartnerId = searchParams.get('partner_page_id');
      if (urlPartnerId) return urlPartnerId;
      return undefined; // 全件表示
    }
    
    // フォールバック: ログイン済みならfactory_idを使用
    return factoryId || undefined;
  };

  const loadCases = async (status: string = '') => {
    if (!isAuthenticated) return;
    setIsLoading(true);
    try {
      const partnerPageId = getPartnerPageIdForApi();
      const fetchedCases = await factoryApi.getCases(status || undefined, partnerPageId);
      setCases(fetchedCases);
    } catch (error: any) {
      console.error('案件取得エラー:', error);
      const errorMessage = error?.response?.data?.error || error?.message || '案件の取得に失敗しました';
      console.error('エラー詳細:', {
        status: error?.response?.status,
        data: error?.response?.data,
        message: error?.message,
      });
      alert(`案件の取得に失敗しました: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadCases(activeStatus);
    }
  }, [activeStatus, isAuthenticated]);

  const handleStatusUpdate = async (caseId: string, status: string) => {
    try {
      // page_idを使用（既存APIとの互換性）
      const caseItem = cases.find((c) => c.id === caseId || c.page_id === caseId);
      const pageId = caseItem?.page_id || caseId;
      
      if (!pageId) {
        alert('❌ 案件IDが見つかりません');
        return;
      }
      
      await factoryApi.updateCaseStatus(pageId, status);
      alert('✅ ステータスを更新しました');
      loadCases(activeStatus); // 再読み込み
    } catch (error) {
      console.error('ステータス更新エラー:', error);
      alert('❌ ステータスの更新に失敗しました');
    }
  };

  const handleCommentAdd = async (caseId: string, comment: string) => {
    try {
      const caseItem = cases.find((c) => c.id === caseId || c.page_id === caseId);
      const pageId = caseItem?.page_id || caseId;
      
      if (!pageId) {
        alert('❌ 案件IDが見つかりません');
        return;
      }
      
      await factoryApi.addComment(pageId, comment);
      alert('✅ コメントを追加しました');
      loadCases(activeStatus); // 再読み込み
    } catch (error) {
      console.error('コメント追加エラー:', error);
      alert('❌ コメントの追加に失敗しました');
    }
  };

  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">認証確認中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* ナビゲーション */}
        <Navigation />

        {/* ヘッダー */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">工場向けダッシュボード</h1>
              {userRole === 'factory' && (
                <p className="text-sm text-blue-600 mt-1">🔒 自社の案件のみ表示中</p>
              )}
            </div>
            <div className="flex gap-4 items-center">
              <button
                onClick={() => setIsManualSearchOpen(true)}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
              >
                📚 作業マニュアルDB検索
              </button>
              <span className="text-sm text-gray-600">
                案件数: <span className="font-semibold">{cases.length}件</span>
              </span>
            </div>
          </div>
        </div>

        {/* 工場マッチング */}
        <div className="mb-6">
          <FactoryMatching />
        </div>

        {/* フィルタ */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">ステータスフィルタ</h2>
          <StatusFilter activeStatus={activeStatus} onStatusChange={setActiveStatus} />
        </div>

        {/* 案件一覧 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">案件一覧</h2>
            <button
              onClick={() => loadCases(activeStatus)}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              🔄 更新
            </button>
          </div>
          <CaseList
            cases={cases}
            isLoading={isLoading}
            onStatusUpdate={handleStatusUpdate}
            onCommentAdd={handleCommentAdd}
          />
        </div>

        {/* 作業マニュアルDB検索モーダル */}
        <ManualSearchModal
          isOpen={isManualSearchOpen}
          onClose={() => setIsManualSearchOpen(false)}
        />
      </div>
    </div>
  );
}

export default function FactoryDashboardPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    }>
      <FactoryDashboardPageContent />
    </Suspense>
  );
}

