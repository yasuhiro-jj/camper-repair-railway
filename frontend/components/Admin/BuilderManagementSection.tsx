'use client';

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

interface Builder {
  id: string;
  name: string;
  prefecture: string;
  address: string;
  phone: string;
  email: string;
  status: string;
}

export default function BuilderManagementSection() {
  const [builders, setBuilders] = useState<Builder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBuilders();
  }, []);

  const fetchBuilders = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const builderList = await adminApi.getBuilders();
      setBuilders(builderList);
    } catch (err: any) {
      console.error('ビルダー一覧の取得に失敗しました:', err);
      setError(err.response?.data?.error || 'ビルダー一覧の取得に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-6 border-l-4 border-purple-500">
      <h2 className="text-xl font-bold text-gray-800 mb-4">🏭 ビルダー管理</h2>

      {error && (
        <div className="bg-red-100 text-red-800 p-4 rounded-lg mb-4 border border-red-300">
          ❌ {error}
        </div>
      )}

      {isLoading ? (
        <div className="text-gray-500">読み込み中...</div>
      ) : builders.length === 0 ? (
        <div className="text-gray-500">ビルダーが見つかりません</div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">名前</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">都道府県</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">電話番号</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">ステータス</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {builders.map((builder, index) => (
                  <tr key={builder.id || `builder-${index}`} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-800">{builder.name}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{builder.prefecture}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{builder.phone}</td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          builder.status === 'アクティブ'
                            ? 'bg-green-100 text-green-800'
                            : builder.status === '休止中'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {builder.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <button
        onClick={fetchBuilders}
        disabled={isLoading}
        className="mt-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white px-6 py-3 rounded-lg font-bold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        🔄 ビルダー一覧更新
      </button>
    </div>
  );
}

