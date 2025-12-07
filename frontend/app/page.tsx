'use client';

import Link from 'next/link';
import Navigation from '@/components/Navigation';

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700">
      <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-center py-16 px-8">
        {/* ナビゲーション */}
        <div className="w-full mb-8">
          <Navigation />
        </div>

        <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-12 shadow-2xl text-center w-full">
          <h1 className="text-4xl font-bold text-purple-600 mb-4">
            🔧 キャンピングカー修理チャットボット
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            AI搭載の修理サポートシステム
          </p>
          
          <div className="flex flex-col gap-4 sm:flex-row justify-center flex-wrap">
            <Link
              href="/chat"
              className="px-8 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-lg font-semibold shadow-lg"
            >
              💬 チャットを開始
            </Link>
            <Link
              href="/partner"
              className="px-8 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-lg font-semibold shadow-lg"
            >
              🔧 修理店を探す
            </Link>
          </div>
          
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 bg-gray-50 rounded-lg">
              <div className="text-3xl mb-2">🔧</div>
              <h3 className="font-semibold text-lg mb-2">AI診断</h3>
              <p className="text-gray-600 text-sm">
                症状を入力するだけで、AIが原因を特定します
              </p>
            </div>
            <div className="p-6 bg-gray-50 rounded-lg">
              <div className="text-3xl mb-2">🔍</div>
              <h3 className="font-semibold text-lg mb-2">修理検索</h3>
              <p className="text-gray-600 text-sm">
                豊富な修理ケースから最適な解決策を見つけます
              </p>
            </div>
            <div className="p-6 bg-gray-50 rounded-lg">
              <div className="text-3xl mb-2">💰</div>
              <h3 className="font-semibold text-lg mb-2">費用目安</h3>
              <p className="text-gray-600 text-sm">
                修理費用の目安を事前に確認できます
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
