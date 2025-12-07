'use client';

export default function Cases() {
  const cases = [
    {
      type: '大工さん',
      title: '大工さんでもできた',
      description: '住宅リフォームの経験を活かして、キャンピングカーの内装修理を開始。月5件程度の依頼で、副収入として安定しています。',
      result: '月間売上：約30万円',
    },
    {
      type: '車屋さん',
      title: '車屋さんで年商300万円アップ',
      description: '自動車整備の技術を活かして、キャンピングカーのエンジン・電装系の修理を担当。既存顧客とは異なる高単価案件で売上向上。',
      result: '年間売上増：300万円',
    },
    {
      type: '公務店',
      title: '公務店が副業的に参入',
      description: '住宅設備工事の経験を活かして、キャンピングカーの水回り・電装工事を担当。週末のみの作業で月10万円程度の副収入を確保。',
      result: '月間売上：約10万円',
    },
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-900">
            事例紹介
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            様々な業種の方がパートナーとして活躍しています
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {cases.map((caseItem, index) => (
              <div
                key={index}
                className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow"
              >
                <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold inline-block mb-4">
                  {caseItem.type}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{caseItem.title}</h3>
                <p className="text-gray-600 mb-4 leading-relaxed">{caseItem.description}</p>
                <div className="bg-green-50 border-l-4 border-green-500 p-3 rounded">
                  <p className="text-green-800 font-bold">{caseItem.result}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

