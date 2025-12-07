'use client';

import { useState } from 'react';
import { adminApi } from '@/lib/api';

export default function DatabaseSection() {
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error' | null; message: string }>({
    type: null,
    message: '',
  });

  const handleReloadDatabase = async () => {
    setIsLoading(true);
    setStatus({ type: null, message: '' });

    try {
      const response = await adminApi.reloadDatabase();
      if (response.success) {
        setStatus({ type: 'success', message: response.message || 'データベースを再構築しました' });
      } else {
        setStatus({ type: 'error', message: response.error || 'データベースの再構築に失敗しました' });
      }
    } catch (error: any) {
      setStatus({
        type: 'error',
        message: error.response?.data?.error || 'エラーが発生しました',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-6 border-l-4 border-blue-500">
      <h2 className="text-xl font-bold text-gray-800 mb-4">📚 データベース管理</h2>
      <p className="text-gray-600 mb-4">
        新しいデータファイルを追加した後、データベースを再構築してください。
      </p>

      <button
        onClick={handleReloadDatabase}
        disabled={isLoading}
        className="bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-lg font-bold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? '🔄 再構築中...' : '🔄 データベース再構築'}
      </button>

      {status.type && (
        <div
          className={`mt-4 p-4 rounded-lg ${
            status.type === 'success'
              ? 'bg-green-100 text-green-800 border border-green-300'
              : 'bg-red-100 text-red-800 border border-red-300'
          }`}
        >
          {status.type === 'success' ? '✅' : '❌'} {status.message}
        </div>
      )}
    </div>
  );
}

