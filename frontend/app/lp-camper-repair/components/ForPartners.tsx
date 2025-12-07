'use client';

export default function ForPartners() {
  const benefits = [
    {
      icon: '💰',
      title: 'キャンピングカーは単価が高い',
      description: '一般の自動車修理と比べて、キャンピングカーの修理は単価が高く、売上が上がりやすい特徴があります。',
      highlight: '平均単価: 15万円〜',
    },
    {
      icon: '📈',
      title: '原価率が低く利益率が高い',
      description: '部品コストが比較的低く、技術力による付加価値が高いため、利益率が優れています。',
      highlight: '利益率: 平均60%以上',
    },
    {
      icon: '🌐',
      title: '依頼は全国から来る',
      description: 'プラットフォームを通じて、全国のキャンピングカー所有者から修理依頼が届きます。',
      highlight: '全国対応可能',
    },
    {
      icon: '⭐',
      title: '既存顧客より質の良い客が多い',
      description: 'キャンピングカー所有者は、適切な修理を求めている真剣な顧客が多い傾向があります。',
      highlight: '成約率が高い',
    },
    {
      icon: '🚀',
      title: '新規事業として導入しやすい',
      description: '既存の技術を活かしながら、新しい市場に参入できるチャンスです。',
      highlight: '初期投資が少ない',
    },
    {
      icon: '🆓',
      title: '登録も無料',
      description: '初期費用や月額費用は一切かかりません。成約時にのみ手数料が発生する成功報酬型です。',
      highlight: '完全無料登録',
    },
  ];

  return (
    <section id="for-partners" className="py-20 bg-slate-900 text-white">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          {/* セクションタイトル */}
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              修理業者向けの強力メリット
            </h2>
            <p className="text-xl text-gray-300">
              キャンピングカー修理は、あなたの事業を成長させる大きなチャンスです
            </p>
          </div>

          {/* メリットグリッド */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {benefits.map((benefit, index) => (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20 hover:bg-white/20 transition-all"
              >
                <div className="text-4xl mb-4">{benefit.icon}</div>
                <h3 className="text-xl font-bold mb-2">{benefit.title}</h3>
                <p className="text-gray-300 mb-4 leading-relaxed">{benefit.description}</p>
                <div className="bg-yellow-400 text-slate-900 px-4 py-2 rounded-lg font-bold text-sm inline-block">
                  {benefit.highlight}
                </div>
              </div>
            ))}
          </div>

          {/* 登録CTA */}
          <div className="bg-white text-slate-900 rounded-lg p-8 text-center">
            <h3 className="text-2xl font-bold mb-4">
              今すぐ登録して、新しい顧客を獲得しましょう
            </h3>
            <p className="text-gray-700 mb-6">
              登録は無料。成約時にのみ手数料が発生する成功報酬型です。
            </p>
            <div className="flex justify-center">
              <a
                href="tel:086-206-6622"
                className="bg-slate-900 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-slate-800 transition-colors shadow-lg border-2 border-slate-900"
              >
                📞 お問い合わせ
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

