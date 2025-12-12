'use client';

import { useState } from 'react';
import Link from 'next/link';
import Navigation from '@/components/Navigation';

export default function RepairAdvicePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const quickSearches = [
    'バッテリー',
    'エアコン',
    'トイレ',
    'FFヒーター',
    '水道ポンプ',
    'インバーター',
  ];

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setSearchQuery(query);
    
    try {
      // Next.jsのAPI Route経由でバックエンドにアクセス（CORS回避）
      const response = await fetch(`/api/repair-advice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('検索結果:', data); // デバッグ用
        setResults(data);
      } else {
        console.error('検索失敗:', response.status); // デバッグ用
        setResults({ error: '検索に失敗しました' });
      }
    } catch (error) {
      console.error('検索エラー:', error);
      setResults({ error: '検索中にエラーが発生しました' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickSearch = (term: string) => {
    handleSearch(term);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-500 via-red-600 to-red-700 p-4">
      <div className="max-w-6xl mx-auto">
        {/* ナビゲーション */}
        <Navigation />

        {/* ヘッダー */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 mb-6 shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-4xl font-bold text-red-600 mb-2">
                🔧 修理アドバイスセンター
              </h1>
              <p className="text-gray-600 text-lg">
                詳細な修理情報と価格データを提供します
              </p>
            </div>
            <Link
              href="/chat"
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all shadow-lg font-semibold"
            >
              ← チャットボットに戻る
            </Link>
          </div>
        </div>

        {/* 検索セクション */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 mb-6 shadow-xl">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">🔍 修理情報検索</h2>
          
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSearch(searchQuery);
            }}
            className="mb-6"
          >
            <div className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="例: バッテリー、雨漏り、エアコン、トイレ、ガスコンロ..."
                className="flex-1 px-6 py-4 border-2 border-red-300 rounded-lg focus:outline-none focus:border-red-500 text-lg"
              />
              <button
                type="submit"
                disabled={isLoading || !searchQuery.trim()}
                className="px-8 py-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                🔍 検索
              </button>
            </div>
          </form>

          {/* クイック検索 */}
          <div>
            <p className="text-gray-600 mb-3 font-medium">よく検索される項目:</p>
            <div className="flex flex-wrap gap-3">
              {quickSearches.map((term) => (
                <button
                  key={term}
                  onClick={() => handleQuickSearch(term)}
                  className="px-5 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-red-100 hover:text-red-700 transition-colors font-medium"
                >
                  {term}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* ローディング */}
        {isLoading && (
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 shadow-xl text-center">
            <div className="flex items-center justify-center gap-4">
              <div className="w-8 h-8 border-4 border-red-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-gray-600 text-lg">生成時間が少々かかりますので、お待ちください...</p>
            </div>
          </div>
        )}

        {/* 検索結果 */}
        {results && !isLoading && (
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 shadow-xl">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">📋 検索結果</h2>
            {results.error ? (
              <div className="text-red-600">{results.error}</div>
            ) : !results.results || results.results.length === 0 ? (
              <div className="text-gray-600 text-center py-8">
                <p className="text-lg mb-2">🔍 検索結果が見つかりませんでした</p>
                <p className="text-sm">別のキーワードで検索してみてください</p>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-gray-600 mb-4">
                  検索結果: {results.total || results.results.length}件
                </p>
                {results.results.map((item: any, index: number) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <h4 className="font-semibold text-lg mb-2 text-red-600">
                      {item.case_id || item.id || `ケース ${index + 1}`}
                    </h4>
                    {item.title && <h5 className="font-medium text-md mb-2">{item.title}</h5>}
                    {item.symptom && (
                      <p className="text-gray-700 mb-2">
                        <span className="font-semibold">症状:</span> {item.symptom}
                      </p>
                    )}
                    {item.description && (
                      <p className="text-gray-600 mb-2">{item.description}</p>
                    )}
                    {item.solution && (
                      <p className="text-gray-700 mb-2">
                        <span className="font-semibold">解決方法:</span> {item.solution}
                      </p>
                    )}
                    {item.cost_estimate && (
                      <p className="text-red-600 font-semibold">
                        💰 費用目安: {item.cost_estimate}
                      </p>
                    )}
                    {item.difficulty && (
                      <p className="text-gray-600 text-sm mt-2">
                        ⚙️ 難易度: {item.difficulty}
                      </p>
                    )}
                    {item.estimated_time && (
                      <p className="text-gray-600 text-sm">
                        ⏱️ 推定時間: {item.estimated_time}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}















