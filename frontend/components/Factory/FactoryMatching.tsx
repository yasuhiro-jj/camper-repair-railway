'use client';

import { useState } from 'react';
import { factoryMatchingApi, CaseInfo, MatchedFactory } from '@/lib/api';

interface FactoryMatchingProps {
  caseInfo?: CaseInfo;
  onFactorySelected?: (factory: MatchedFactory) => void;
}

export default function FactoryMatching({ caseInfo, onFactorySelected }: FactoryMatchingProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [matchedFactories, setMatchedFactories] = useState<MatchedFactory[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<CaseInfo>({
    category: caseInfo?.category || '',
    user_message: caseInfo?.user_message || '',
    customer_location: caseInfo?.customer_location || caseInfo?.prefecture || '',
  });

  const handleMatch = async () => {
    setIsLoading(true);
    setError(null);
    setMatchedFactories([]);

    try {
      const factories = await factoryMatchingApi.matchFactories(formData, 5);
      setMatchedFactories(factories);

      if (factories.length === 0) {
        setError('マッチする工場が見つかりませんでした');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'マッチングに失敗しました');
      console.error('マッチングエラー:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAutoAssign = async (caseId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const assignedFactory = await factoryMatchingApi.autoAssignCase(caseId, formData);

      if (assignedFactory) {
        setMatchedFactories([assignedFactory]);
        if (onFactorySelected) {
          onFactorySelected(assignedFactory);
        }
      } else {
        setError('自動割り当てに失敗しました');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || '自動割り当てに失敗しました');
      console.error('自動割り当てエラー:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">🏭 工場マッチング</h2>

      {/* フォーム */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            カテゴリ
          </label>
          <input
            type="text"
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            placeholder="例: エアコン、バッテリー、水回り"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            症状・メッセージ
          </label>
          <textarea
            value={formData.user_message}
            onChange={(e) => setFormData({ ...formData, user_message: e.target.value })}
            placeholder="例: エアコンが効かない、冷房が効かない"
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            所在地（都道府県）
          </label>
          <input
            type="text"
            value={formData.customer_location}
            onChange={(e) => setFormData({ ...formData, customer_location: e.target.value })}
            placeholder="例: 東京都、大阪府"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* ボタン */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={handleMatch}
          disabled={isLoading}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'マッチング中...' : '🔍 工場を検索'}
        </button>
        <button
          onClick={() => handleAutoAssign('AUTO-' + Date.now())}
          disabled={isLoading}
          className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? '割り当て中...' : '⚡ 自動割り当て'}
        </button>
      </div>

      {/* エラー表示 */}
      {error && (
        <div className="bg-red-100 text-red-800 p-4 rounded-lg mb-4 border border-red-300">
          ❌ {error}
        </div>
      )}

      {/* マッチング結果 */}
      {matchedFactories.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            マッチング結果 ({matchedFactories.length}件)
          </h3>

          {matchedFactories.map((factory, index) => (
            <div
              key={factory.factory_id || index}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-bold text-lg text-gray-900">
                    {factory.factory_id} - {factory.name}
                  </h4>
                  <p className="text-sm text-gray-600">
                    📍 {factory.prefecture}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-600">
                    {(factory.matching_score * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500">マッチングスコア</div>
                </div>
              </div>

              {factory.specialties && factory.specialties.length > 0 && (
                <div className="mb-2">
                  <span className="text-sm text-gray-600">専門分野: </span>
                  <span className="text-sm font-medium">
                    {factory.specialties.join(', ')}
                  </span>
                </div>
              )}

              {factory.score_details && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-gray-600">地域: </span>
                      <span className="font-medium">
                        {(factory.score_details.location_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">専門分野: </span>
                      <span className="font-medium">
                        {(factory.score_details.specialty_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">混雑状況: </span>
                      <span className="font-medium">
                        {(factory.score_details.workload_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">評価: </span>
                      <span className="font-medium">
                        {(factory.score_details.rating_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {onFactorySelected && (
                <button
                  onClick={() => onFactorySelected(factory)}
                  className="mt-3 w-full px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
                >
                  この工場を選択
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

