'use client';

export default function Hero() {
  return (
    <section className="relative bg-gradient-to-br from-green-600 via-green-700 to-emerald-800 text-white py-20 md:py-32">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center">
          {/* メインキャッチコピー */}
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            キャンピングカー修理ができる業者さん募集！
            <br />
            <span className="text-yellow-300">専門業者でなくてもOKです。</span>
          </h1>

          {/* サブコピー */}
          <p className="text-xl md:text-2xl mb-8 text-green-100 leading-relaxed">
            大工・公務店・自動車整備工場・個人職人の方も歓迎。
            <br />
            全国からの修理依頼をあなたの会社に送客します。
          </p>

          {/* CTAボタン */}
          <div className="flex flex-col gap-4 justify-center items-center">
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <a
                href="#form"
                className="bg-yellow-400 text-green-900 px-8 py-4 rounded-lg font-bold text-lg hover:bg-yellow-300 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 min-w-[280px] text-center"
              >
                ✨ 無料でパートナー登録する
              </a>
              <a
                href="tel:086-206-6622"
                className="bg-white text-green-700 px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 min-w-[280px] text-center"
              >
                📞 まずは話を聞いてみる
              </a>
            </div>
            <a
              href="https://camper-repair.net/contact/"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white text-green-700 px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 min-w-[280px] text-center"
            >
              📧 メールで聞いてみる
            </a>
          </div>

          {/* 統計情報 */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <div className="text-3xl font-bold text-yellow-300 mb-2">数万円から20万円以上</div>
              <div className="text-sm text-green-100">平均単価</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <div className="text-3xl font-bold text-yellow-300 mb-2">全国</div>
              <div className="text-sm text-green-100">対応エリア</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

