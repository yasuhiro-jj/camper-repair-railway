'use client';

export default function Flow() {
  // チャットアイコン
  const ChatIcon = () => (
    <svg className="w-12 h-12 mx-auto text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  );

  // AI診断アイコン
  const AIIcon = () => (
    <svg className="w-12 h-12 mx-auto text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  );

  // マッチングアイコン
  const MatchingIcon = () => (
    <svg className="w-12 h-12 mx-auto text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  );

  // 電話アイコン
  const PhoneIcon = () => (
    <svg className="w-12 h-12 mx-auto text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
    </svg>
  );

  // チェックマークアイコン
  const CheckIcon = () => (
    <svg className="w-12 h-12 mx-auto text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );

  const steps = [
    {
      number: '1',
      title: 'チャットボットで症状入力',
      description: '故障の症状をチャットボットに入力します。簡単な質問に答えるだけでOK。',
      icon: <ChatIcon />,
    },
    {
      number: '2',
      title: 'AIがほぼ正確に故障診断',
      description: 'AIが症状を分析し、故障箇所と修理内容を特定。見積もりも自動で生成されます。',
      icon: <AIIcon />,
    },
    {
      number: '3',
      title: '最適な修理工場を選定',
      description: 'プラットフォームが、地域・スキル・稼働状況を考慮して最適な工場を選定します。',
      icon: <MatchingIcon />,
    },
    {
      number: '4',
      title: '工場と直接やり取り',
      description: '選定された工場と直接連絡を取り、修理の詳細を確認。日程や費用を相談します。',
      icon: <PhoneIcon />,
    },
    {
      number: '5',
      title: '修理完了',
      description: '工場で修理が完了。キャンピングカーが正常に動作するようになります。',
      icon: <CheckIcon />,
    },
  ];

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-5xl mx-auto">
          {/* セクションタイトル */}
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-slate-900">
            利用の流れ
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            5つのステップで、簡単に修理業者を見つけられます
          </p>

          {/* フローチャート */}
          <div className="relative">
            {/* デスクトップ用の線 */}
            <div className="hidden md:block absolute top-1/2 left-0 right-0 h-1 bg-yellow-400 transform -translate-y-1/2 z-0"></div>

            {/* ステップカード */}
            <div className="grid md:grid-cols-5 gap-6 relative z-10">
              {steps.map((step, index) => (
                <div key={index} className="relative">
                  {/* ステップ番号バッジ */}
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-20">
                    <div className="bg-yellow-400 text-slate-900 w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl shadow-lg border-4 border-white">
                      {step.number}
                    </div>
                  </div>

                  {/* カード */}
                  <div className="bg-white border-2 border-gray-200 rounded-lg p-6 mt-8 hover:shadow-lg transition-shadow">
                    <div className="mb-4">{step.icon}</div>
                    <h3 className="text-lg font-bold text-slate-900 mb-2 text-center">
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
                        className="w-6 h-6 text-yellow-400"
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

          {/* CTA */}
          <div className="mt-12 text-center">
            <a
              href="/chat"
              className="inline-block bg-slate-900 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-slate-800 transition-colors shadow-lg"
            >
              🚀 今すぐ無料診断を始める
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

