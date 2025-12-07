'use client';

import Link from 'next/link';
import ChatWindow from '@/components/Chat/ChatWindow';
import Navigation from '@/components/Navigation';

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700 p-3">
      <div className="max-w-6xl mx-auto">
        {/* ナビゲーション */}
        <Navigation />

        {/* ヘッダー */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-5 mb-4 shadow-xl text-center">
          <h1 className="text-2xl font-bold text-purple-600 mb-2">
            🔧 キャンピングカー修理チャットボット
          </h1>
          <p className="text-gray-600 text-base mb-3">
            AI診断 + リアルタイム情報 + 専門知識 = 修理支援
          </p>
          <div className="flex justify-center gap-3 flex-wrap">
            <Link
              href="/partner"
              className="inline-block px-5 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-semibold"
            >
              🔧 修理店を探す
            </Link>
            <Link
              href="/lp-partner-recruit"
              className="inline-block px-5 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-semibold"
            >
              🏭 パートナー募集
            </Link>
          </div>
        </div>

        {/* チャットウィンドウ */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-4 shadow-xl flex flex-col" style={{ height: 'calc(100vh - 240px)', minHeight: '450px' }}>
          <ChatWindow />
        </div>
      </div>
    </div>
  );
}
