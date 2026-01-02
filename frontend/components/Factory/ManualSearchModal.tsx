'use client';

import { useState } from 'react';
import { manualApi, Manual } from '@/lib/api';

interface ManualSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialQuery?: string;
}

export default function ManualSearchModal({
  isOpen,
  onClose,
  initialQuery = '',
}: ManualSearchModalProps) {
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [category, setCategory] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [manuals, setManuals] = useState<Manual[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('検索キーワードを入力してください');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await manualApi.searchManuals(
        searchQuery,
        category || undefined,
        difficulty || undefined,
        20
      );
      setManuals(result.manuals);
    } catch (err: any) {
      console.error('マニュアル検索エラー:', err);
      setError(err?.response?.data?.error || 'マニュアルの検索に失敗しました');
      setManuals([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* ヘッダー */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">作業マニュアルDB検索</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* 検索フォーム */}
        <div className="p-6 border-b bg-gray-50">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                検索キーワード
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="症状、修理内容、部品名などで検索"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  onClick={handleSearch}
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
                >
                  {isLoading ? '検索中...' : '🔍 検索'}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  カテゴリ
                </label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  placeholder="例: エアコン、バッテリー"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  難易度
                </label>
                <input
                  type="text"
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  placeholder="例: 初級、中級、上級"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* エラーメッセージ */}
        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-500">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* 検索結果 */}
        <div className="flex-1 overflow-y-auto p-6">
          {manuals.length === 0 && !isLoading && !error && (
            <div className="text-center text-gray-500 py-12">
              <p>検索キーワードを入力して検索してください</p>
              <p className="text-sm mt-2">約1000件の作業マニュアルから検索できます</p>
            </div>
          )}

          {isLoading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-600">検索中...</p>
            </div>
          )}

          {manuals.length > 0 && (
            <div className="space-y-4">
              <div className="text-sm text-gray-600 mb-4">
                検索結果: {manuals.length}件
              </div>
              {manuals.map((manual) => (
                <div
                  key={manual.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {manual.title || manual.manual_id || 'タイトルなし'}
                    </h3>
                    <div className="flex gap-2">
                      {manual.category && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {manual.category}
                        </span>
                      )}
                      {manual.difficulty && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                          {manual.difficulty}
                        </span>
                      )}
                    </div>
                  </div>
                  {manual.steps && (
                    <div className="text-sm text-gray-700 mb-2">
                      <strong>作業手順:</strong>
                      <div className="mt-1 whitespace-pre-wrap">{manual.steps}</div>
                    </div>
                  )}
                  {manual.parts && (
                    <div className="text-sm text-gray-700 mb-2">
                      <strong>必要な部品:</strong> {manual.parts}
                    </div>
                  )}
                  {manual.time_estimate && (
                    <div className="text-sm text-gray-700">
                      <strong>修理時間の目安:</strong> {manual.time_estimate}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* フッター */}
        <div className="p-4 border-t bg-gray-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            閉じる
          </button>
        </div>
      </div>
    </div>
  );
}





















