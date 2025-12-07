'use client';

import Link from 'next/link';

export default function Hero() {
  return (
    <section className="relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white min-h-screen flex items-center">
      {/* 背景パターン */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(255,255,255,.05) 35px, rgba(255,255,255,.05) 70px)'
        }}></div>
      </div>

      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* メインキャッチコピー */}
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            全国どこでも修理可能。
            <br />
            <span className="text-yellow-400 text-3xl md:text-5xl">キャンピングカーの &quot;困った&quot;</span>
            <br />
            を最短で解決。
          </h1>

          {/* サブコピー */}
          <p className="text-xl md:text-2xl mb-8 text-gray-200 leading-relaxed">
            修理工場・大工・公務店・自動車整備工場までカバー
            <br />
            あなたの車に合う最適な修理業者をAIが自動マッチング
          </p>

          {/* CTAボタン */}
          <div className="flex justify-center items-center">
            <Link
              href="/chat"
              className="bg-yellow-400 text-slate-900 px-8 py-4 rounded-lg font-bold text-lg hover:bg-yellow-300 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 min-w-[280px] text-center"
            >
              🚀 いますぐ無料診断
            </Link>
          </div>
        </div>
      </div>

      {/* スクロールインジケーター */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </section>
  );
}

