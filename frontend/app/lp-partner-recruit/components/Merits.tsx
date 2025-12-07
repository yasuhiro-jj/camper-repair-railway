'use client';

export default function Merits() {
  const merits = [
    {
      icon: '🌐',
      title: '全国から修理依頼が自動で届く',
      description: 'AIマッチングにより、あなたのエリアとスキルに合った案件が自動的に届きます。',
    },
    {
      icon: '⭐',
      title: '高単価（1件3〜20万円）',
      description: '一般の自動車修理と比べて単価が高く、効率的に売上を上げられます。',
    },
    {
      icon: '📈',
      title: 'キャンピングカー修理は他の車種より利益率が高い',
      description: 'キャンピングカー修理は他の車種より利益率が高い',
    },
    {
      icon: '🌊',
      title: 'キャンピングカー業界は職人不足のブルーオーシャン',
      description: '競合が少なく、安定した需要がある市場です。',
    },
    {
      icon: '⚡',
      title: 'AIが一次診断→案件化するので現場が楽',
      description: '事前診断により、現場での判断が不要で作業に集中できます。',
    },
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-green-50 to-emerald-50">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-900">
            パートナーになるメリット
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            5つの強力なメリットで、あなたの事業を成長させます
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {merits.map((merit, index) => (
              <div
                key={index}
                className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow border-t-4 border-green-500"
              >
                <div className="text-4xl mb-4">{merit.icon}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{merit.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{merit.description}</p>
              </div>
            ))}
          </div>

          {/* CTA */}
          <div className="mt-12 text-center">
            <div className="flex flex-col gap-4 justify-center items-center">
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <a
                  href="#form"
                  className="inline-block bg-green-600 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-700 transition-colors shadow-lg"
                >
                  🚀 今すぐ無料登録する
                </a>
                <a
                  href="tel:086-206-6622"
                  className="inline-block bg-white text-green-700 px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 min-w-[280px] text-center border-2 border-green-700"
                >
                  📞 まずは話を聞いてみる
                </a>
              </div>
              <a
                href="https://camper-repair.net/contact/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-white text-green-700 px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 min-w-[280px] text-center border-2 border-green-700"
              >
                📧 メールで聞いてみる
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

