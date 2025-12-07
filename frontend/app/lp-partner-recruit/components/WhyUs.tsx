'use client';

export default function WhyUs() {
  const reasons = [
    {
      icon: '🏠',
      title: 'キャンピングカー修理の多くは住宅設備に似ている',
      description: '雨漏り・家具修理・電装・水回りなど、住宅設備の技術がそのまま活かせます。',
      examples: ['雨漏り修理', '家具・内装の修繕', '電装工事', '水回り設備'],
    },
    {
      icon: '📈',
      title: '特殊技術が必要なのは全体の20%程度',
      description: 'キャンピングカー特有の技術が必要な案件は少なく、基本的な技術があれば対応可能です。',
      examples: ['80%は一般技術で対応可能', '残り20%はマニュアル提供'],
    },
    {
      icon: '🔍',
      title: 'AI診断が一次切り分けしてくれるため、現場は迷わない',
      description: 'AIが事前に故障箇所と難易度を判定するため、現場での判断が不要です。',
      examples: ['故障箇所の自動特定', '難易度の自動判定', '必要な部品の提示'],
    },
  ];

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-900">
            なぜ "非キャンピングカー修理業者"<br />
            でもできるのか
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            キャンピングカー修理は、実は身近な技術で対応できることが多いのです
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            {reasons.map((reason, index) => (
              <div
                key={index}
                className="bg-gray-50 rounded-lg p-8 border-l-4 border-green-500 hover:shadow-lg transition-shadow"
              >
                <div className="text-5xl mb-4">{reason.icon}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{reason.title}</h3>
                <p className="text-gray-700 mb-4 leading-relaxed">{reason.description}</p>
                <ul className="space-y-2">
                  {reason.examples.map((example, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                      <span className="text-green-500 mt-1">✓</span>
                      <span>{example}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

