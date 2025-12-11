'use client';

import { useState } from 'react';
import Link from 'next/link';
import Navigation from '@/components/Navigation';

// デフォルトはRailwayのURL（Vercel本番環境用）
// 開発環境では環境変数 NEXT_PUBLIC_API_URL=http://localhost:5002 を設定
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'https://web-development-8c2f.up.railway.app';

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
      const response = await fetch(`${API_BASE_URL}/api/repair_advice/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setResults(data);
      } else {
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
            ) : (
              <div className="space-y-4">
                {results.repair_cases && results.repair_cases.length > 0 && (
                  <div>
                    <h3 className="text-xl font-semibold mb-4">🔧 関連修理ケース</h3>
                    <div className="space-y-3">
                      {results.repair_cases.map((case_: any, index: number) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                          <h4 className="font-semibold text-lg mb-2">{case_.title || case_.name}</h4>
                          {case_.description && <p className="text-gray-600 mb-2">{case_.description}</p>}
                          {case_.cost_estimate && (
                            <p className="text-red-600 font-semibold">💰 費用目安: {case_.cost_estimate}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {results.parts && results.parts.length > 0 && (
                  <div>
                    <h3 className="text-xl font-semibold mb-4">🛠️ 必要な部品・工具</h3>
                    <div className="space-y-2">
                      {results.parts.map((part: any, index: number) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-3">
                          <p className="font-medium">{part.name}</p>
                          {part.price && <p className="text-gray-600 text-sm">価格: {part.price}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {results.answer && (
                  <div className="border-l-4 border-red-500 pl-4">
                    <h3 className="text-xl font-semibold mb-2">💡 アドバイス</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{results.answer}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}















