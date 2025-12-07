'use client';

import { useState, useEffect } from 'react';
import { adminApi } from '@/lib/api';

interface SystemInfo {
  dbStatus: string;
  docCount: number;
}

export default function SystemInfoSection() {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSystemInfo = async () => {
      setIsLoading(true);
      try {
        const info = await adminApi.getSystemInfo();
        setSystemInfo(info);
      } catch (error) {
        console.error('システム情報の取得に失敗しました:', error);
        setSystemInfo({
          dbStatus: 'エラー',
          docCount: 0,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchSystemInfo();
  }, []);

  return (
    <div className="bg-gray-50 rounded-lg p-6 border-l-4 border-blue-500">
      <h2 className="text-xl font-bold text-gray-800 mb-4">⚙️ システム情報</h2>
      {isLoading ? (
        <p className="text-gray-500">確認中...</p>
      ) : systemInfo ? (
        <div className="space-y-2">
          <p>
            <strong className="text-gray-700">データベース状態:</strong>{' '}
            <span className="text-gray-600">{systemInfo.dbStatus}</span>
          </p>
          <p>
            <strong className="text-gray-700">読み込み済みドキュメント数:</strong>{' '}
            <span className="text-gray-600">{systemInfo.docCount}個</span>
          </p>
        </div>
      ) : (
        <p className="text-gray-500">情報を取得できませんでした</p>
      )}
    </div>
  );
}

