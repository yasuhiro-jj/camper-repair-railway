'use client';

export default function Flow() {
  const steps = [
    {
      number: '1',
      title: 'ユーザーがAIチャットで相談',
      description: 'キャンピングカー所有者が症状をAIチャットに入力します。',
      icon: '💬',
    },
    {
      number: '2',
      title: 'AIが故障個所・難易度を自動判定',
      description: 'AIが症状を分析し、キャンピングカー専門業者でなければできない作業と、一般の車両修理でも対応できる案件を自動で振り分けます。',
      icon: '🔍',
    },
    {
      number: '3',
      title: 'パートナーに案件が自動通知',
      description: 'あなたのエリアとスキルに合った案件が自動的に通知されます。',
      icon: '📨',
    },
    {
      number: '4',
      title: '見積もり＆修理',
      description: '見積もりを提出し、承認後、修理を実施します。',
      icon: '🔧',
    },
    {
      number: '5',
      title: '手数料を引いた金額をパートナー様へ送金',
      description: '売上一旦サポートセンターに入金してもらい、手数料を引いた金額を後日パートナー様へ送金致します',
      icon: '💰',
    },
  ];

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-900">
            修理依頼の流れ
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            5つのステップで、スムーズに修理案件を受注できます
          </p>

          {/* フローチャート */}
          <div className="relative">
            {/* デスクトップ用の線 */}
            <div className="hidden md:block absolute top-1/2 left-0 right-0 h-1 bg-green-400 transform -translate-y-1/2 z-0"></div>

            {/* ステップカード */}
            <div className="grid md:grid-cols-5 gap-6 relative z-10">
              {steps.map((step, index) => (
                <div key={index} className="relative">
                  {/* ステップ番号バッジ */}
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-20">
                    <div className="bg-green-500 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl shadow-lg border-4 border-white">
                      {step.number}
                    </div>
                  </div>

                  {/* カード */}
                  <div className="bg-white border-2 border-gray-200 rounded-lg p-6 mt-8 hover:shadow-lg transition-shadow">
                    <div className="text-4xl text-center mb-4">{step.icon}</div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2 text-center">
                      {step.title}
                    </h3>
                    <p className="text-sm text-gray-600 text-center leading-relaxed">
                      {step.description}
                    </p>
                  </div>

                  {/* 矢印（最後以外） */}
                  {index < steps.length - 1 && (
                    <div className="hidden md:block absolute top-1/2 -right-3 z-10">
                      <svg
                        className="w-6 h-6 text-green-500"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

