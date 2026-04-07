'use client';

import { useState, useEffect, Suspense, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { FactoryCase } from '@/types';
import { factoryApi } from '@/lib/api';
import { useAuthGuard } from '@/lib/authGuard';
import CaseList from '@/components/Factory/CaseList';
import StatusFilter from '@/components/Factory/StatusFilter';
import ManualSearchModal from '@/components/Factory/ManualSearchModal';
import FactoryMatchingPanel from '@/components/Factory/FactoryMatchingPanel';
import Navigation from '@/components/Navigation';

function FactoryDashboardPageContent() {
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: isAuthLoading } = useAuthGuard();
  const [cases, setCases] = useState<FactoryCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeStatus, setActiveStatus] = useState<string>('');
  const [isManualSearchOpen, setIsManualSearchOpen] = useState(false);
  const [userRole, setUserRole] = useState<string | null>(null);
  const [factoryName, setFactoryName] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setUserRole(localStorage.getItem('role'));
      setFactoryName(localStorage.getItem('factory_name'));
    }
  }, [isAuthenticated]);

  const statusSummary = useMemo(() => {
    const keys = ['受付', '診断中', '修理中', '完了', 'キャンセル'] as const;
    const counts: Record<string, number> = {};
    for (const k of keys) counts[k] = 0;
    for (const c of cases) {
      const s = (c.status || '').trim();
      if (s in counts) counts[s]++;
    }
    const inProgress = (counts['診断中'] || 0) + (counts['修理中'] || 0);
    return { total: cases.length, counts, inProgress };
  }, [cases]);
  
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

  const fetchCasesSnapshot = async (status: string = ''): Promise<FactoryCase[]> => {
    const partnerPageId = getPartnerPageIdForApi();
    return factoryApi.getCases(status || undefined, partnerPageId);
  };

  const loadCases = async (status: string = '', silent: boolean = false): Promise<FactoryCase[] | undefined> => {
    if (!isAuthenticated) return;
    if (!silent) {
      setIsLoading(true);
    }
    try {
      const fetchedCases = await fetchCasesSnapshot(status);
      setCases(fetchedCases);
      return fetchedCases;
    } catch (error: any) {
      if (silent) {
        console.warn('案件一覧の再同期に失敗しました:', error);
        return;
      }
      console.error('案件取得エラー:', error);
      const errorMessage = error?.response?.data?.error || error?.message || '案件の取得に失敗しました';
      console.error('エラー詳細:', {
        status: error?.response?.status,
        data: error?.response?.data,
        message: error?.message,
      });
      alert(`案件の取得に失敗しました: ${errorMessage}`);
    } finally {
      if (!silent) {
        setIsLoading(false);
      }
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadCases(activeStatus);
    }
  }, [activeStatus, isAuthenticated]);

  const getOptimisticCases = (
    currentCases: FactoryCase[],
    targetCaseId: string,
    nextStatus: string,
    currentFilter: string,
  ) => {
    const updatedCases = currentCases.map((c) => {
      if (c.id === targetCaseId || c.page_id === targetCaseId) {
        return {
          ...c,
          status: nextStatus,
          updatedAt: new Date().toISOString(),
        };
      }
      return c;
    });

    if (currentFilter && nextStatus !== currentFilter) {
      return updatedCases.filter((c) => !(c.id === targetCaseId || c.page_id === targetCaseId));
    }

    return updatedCases;
  };

  const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

  const verifyStatusUpdate = async (caseId: string, expectedStatus: string): Promise<boolean> => {
    const normalizedStatus = expectedStatus.trim();
    const retryDelays = [0, 800, 1600];

    for (const delay of retryDelays) {
      if (delay > 0) {
        await sleep(delay);
      }

      try {
        const snapshot = await fetchCasesSnapshot();
        const latestCase = snapshot.find((c) => c.id === caseId || c.page_id === caseId);
        if ((latestCase?.status || '').trim() === normalizedStatus) {
          return true;
        }
      } catch (verifyError) {
        console.warn('ステータス更新後の再確認に失敗しました:', verifyError);
      }
    }

    return false;
  };

  const handleStatusUpdate = async (caseId: string, status: string) => {
    const previousCases = cases;
    try {
      // page_idを使用（既存APIとの互換性）
      const caseItem = previousCases.find((c) => c.id === caseId || c.page_id === caseId);
      const pageId = caseItem?.page_id || caseId;
      
      if (!pageId) {
        alert('❌ 案件IDが見つかりません');
        return;
      }

      if (caseItem?.status === status) {
        return;
      }

      setCases(getOptimisticCases(previousCases, caseId, status, activeStatus));
      await factoryApi.updateCaseStatus(pageId, status);

      // 保存完了後に裏で再同期し、Notion側の最終状態を反映する
      void loadCases(activeStatus, true);
    } catch (error) {
      console.error('ステータス更新エラー:', error);
      if (await verifyStatusUpdate(caseId, status)) {
        console.warn('ステータス更新レスポンスは失敗扱いでしたが、再確認時点では更新済みでした');
        void loadCases(activeStatus, true);
        return;
      }

      setCases(previousCases);
      alert('❌ ステータスの更新に失敗しました');
    }
  };

  const handleCommentAdd = async (
    caseId: string,
    comment: string,
    notifyCustomerEmail?: boolean,
  ) => {
    try {
      const caseItem = cases.find((c) => c.id === caseId || c.page_id === caseId);
      const pageId = caseItem?.page_id || caseId;
      
      if (!pageId) {
        alert('❌ 案件IDが見つかりません');
        return;
      }
      
      const { emailSent } = await factoryApi.addComment(pageId, comment, notifyCustomerEmail);
      if (notifyCustomerEmail) {
        if (emailSent === true) {
          alert('✅ コメントを追加し、お客様へメールを送信しました');
        } else if (emailSent === false) {
          alert(
            '✅ コメントは保存しました。メールは送信できませんでした（アドレス未設定・または送信設定を確認してください）',
          );
        } else {
          alert('✅ コメントを追加しました');
        }
      } else {
        alert('✅ コメントを追加しました');
      }
      loadCases(activeStatus); // 再読み込み
    } catch (error) {
      console.error('コメント追加エラー:', error);
      alert('❌ コメントの追加に失敗しました');
    }
  };

  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-100 via-gray-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-slate-300 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">認証確認中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-100 via-gray-50 to-slate-100 p-4 pb-10">
      <div className="max-w-7xl mx-auto">
        {/* ナビゲーション */}
        <Navigation />

        {/* 管理者のみ：統計付きの大きなヘッダー。工場アカウントは下のコンパクトバーのみ */}
        {userRole === 'admin' ? (
          <header className="relative mb-6 overflow-hidden rounded-2xl border border-slate-200/90 bg-white p-6 shadow-sm">
            <div className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-blue-600 via-blue-500 to-emerald-500" />
            <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Factory</p>
                <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                  工場向けダッシュボード
                </h1>
                {factoryName && (
                  <p className="mt-1 truncate text-sm font-medium text-slate-700">{factoryName}</p>
                )}
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <span className="inline-flex items-center rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-800 ring-1 ring-inset ring-violet-200">
                    管理者
                  </span>
                </div>
              </div>
              <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:items-center sm:justify-end">
                <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:justify-end">
                  <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-center sm:text-left">
                    <p className="text-[10px] font-medium uppercase text-slate-500">全件</p>
                    <p className="text-lg font-semibold tabular-nums text-slate-900">{statusSummary.total}</p>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-center sm:text-left">
                    <p className="text-[10px] font-medium uppercase text-slate-500">進行中</p>
                    <p className="text-lg font-semibold tabular-nums text-slate-900">{statusSummary.inProgress}</p>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-center sm:text-left">
                    <p className="text-[10px] font-medium uppercase text-slate-500">受付</p>
                    <p className="text-lg font-semibold tabular-nums text-slate-900">
                      {statusSummary.counts['受付'] ?? 0}
                    </p>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-center sm:text-left">
                    <p className="text-[10px] font-medium uppercase text-slate-500">完了</p>
                    <p className="text-lg font-semibold tabular-nums text-slate-900">
                      {statusSummary.counts['完了'] ?? 0}
                    </p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 sm:justify-end">
                  <button
                    type="button"
                    onClick={() => setIsManualSearchOpen(true)}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
                  >
                    作業マニュアル検索
                  </button>
                  <button
                    type="button"
                    onClick={() => loadCases(activeStatus)}
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-800 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    一覧を更新
                  </button>
                </div>
              </div>
            </div>
          </header>
        ) : (
          <div className="mb-6 flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              {factoryName ? (
                <p className="truncate text-base font-semibold text-slate-900">{factoryName}</p>
              ) : (
                <p className="text-base font-semibold text-slate-900">工場ダッシュボード</p>
              )}
              <p className="mt-0.5 text-xs text-slate-500">自社の案件のみ表示しています</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => setIsManualSearchOpen(true)}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
              >
                作業マニュアル検索
              </button>
              <button
                type="button"
                onClick={() => loadCases(activeStatus)}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-800 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                一覧を更新
              </button>
            </div>
          </div>
        )}

        {userRole === 'admin' && <FactoryMatchingPanel />}

        {/* フィルタ */}
        <section className="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm mb-6">
          <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-base font-semibold text-slate-900">ステータスで絞り込み</h2>
              <p className="text-sm text-slate-500">タップでフィルタを切り替えます</p>
            </div>
          </div>
          <StatusFilter activeStatus={activeStatus} onStatusChange={setActiveStatus} />
        </section>

        {/* 案件一覧 */}
        <section className="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm">
          <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-base font-semibold text-slate-900">案件一覧</h2>
              <p className="text-sm text-slate-500">
                {activeStatus ? `「${activeStatus}」の案件` : 'すべての案件'}
              </p>
            </div>
            <p className="text-sm text-slate-600">
              表示件数: <span className="font-semibold tabular-nums text-slate-900">{cases.length}</span> 件
            </p>
          </div>
          <CaseList
            cases={cases}
            isLoading={isLoading}
            onStatusUpdate={handleStatusUpdate}
            onCommentAdd={handleCommentAdd}
          />
        </section>

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
      <div className="min-h-screen bg-gradient-to-b from-slate-100 via-gray-50 to-slate-100 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-slate-300 border-t-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">読み込み中...</p>
        </div>
      </div>
    }>
      <FactoryDashboardPageContent />
    </Suspense>
  );
}

