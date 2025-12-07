'use client';

import Link from 'next/link';
import Navigation from '@/components/Navigation';
import DatabaseSection from '@/components/Admin/DatabaseSection';
import SystemInfoSection from '@/components/Admin/SystemInfoSection';
import BuilderManagementSection from '@/components/Admin/BuilderManagementSection';

export default function AdminPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* ナビゲーション */}
        <Navigation />

        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl p-6 md:p-8 space-y-6">
          <h1 className="text-3xl md:text-4xl font-bold text-center text-gray-800 mb-8">
            🔧 キャンピングカー修理チャットボット管理画面
          </h1>

          {/* データベース管理 */}
          <DatabaseSection />

          {/* システム情報 */}
          <SystemInfoSection />

          {/* ビルダー管理 */}
          <BuilderManagementSection />

        </div>
      </div>
    </div>
  );
}

