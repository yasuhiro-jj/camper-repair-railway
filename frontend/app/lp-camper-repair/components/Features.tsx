'use client';

export default function Features() {
  // AI診断アイコン（SVG）
  const AIIcon = () => (
    <svg className="w-16 h-16 mx-auto mb-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  );

  // 工場ネットワークアイコン（SVG）
  const FactoryIcon = () => (
    <svg className="w-16 h-16 mx-auto mb-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    </svg>
  );

  // マッチングアイコン（SVG）
  const MatchingIcon = () => (
    <svg className="w-16 h-16 mx-auto mb-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  );

  const features = [
    {
      icon: <AIIcon />,
      title: 'AI一次診断 → 故障内容を可視化',
      description: 'あなたのチャットボットと連動し、故障箇所・部品・工賃の見積もりを自動で生成。症状を入力するだけで、AIが正確に診断し、必要な修理内容を明確にします。',
      details: [
        'チャットボットで症状を入力',
        'AIが故障箇所を特定',
        '必要な部品と工賃を自動見積もり',
        '修理内容を可視化して提示',
      ],
    },
    {
      icon: <FactoryIcon />,
      title: '全国の修理工場・大工・公務店と連携',
      description: '車屋でなくても歓迎。電気・水回りに強い大工も登録できる、キャンピングカーに特化しない広い受け皿を用意しています。',
      details: [
        '修理工場・自動車整備工場',
        '大工・工務店',
        '電気工事士',
        '水回り専門業者',
      ],
    },
    {
      icon: <MatchingIcon />,
      title: '依頼者と業者をAIで自動マッチング',
      description: '近い業者、スキルが合う業者、忙しくない業者を自動選択。最適なマッチングで、スムーズな修理を実現します。',
      details: [
        '地域に基づく自動マッチング',
        '専門スキルによる最適化',
        '工場の稼働状況を考慮',
        '最短での修理完了を実現',
      ],
    },
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          {/* セクションタイトル */}
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-slate-900">
            プラットフォームの特徴
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            3つの強力な機能で、キャンピングカー修理を徹底サポート
          </p>

          {/* 機能カード */}
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow border-t-4 border-yellow-400"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold text-slate-900 mb-4 text-center">
                  {feature.title}
                </h3>
                <p className="text-gray-700 mb-6 leading-relaxed">
                  {feature.description}
                </p>
                <ul className="space-y-2">
                  {feature.details.map((detail, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                      <span className="text-yellow-400 mt-1">✓</span>
                      <span>{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* CTA */}
          <div className="mt-12 text-center">
            <a
              href="/chat"
              className="inline-block bg-slate-900 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-slate-800 transition-colors shadow-lg"
            >
              🚀 無料診断を始める
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

