'use client';

export default function FAQ() {
  const faqs = [
    {
      question: '専門知識なくてもできますか？',
      answer: 'はい、できます。キャンピングカー修理の多くは住宅設備や自動車整備の技術で対応可能です。わからない作業については、詳細なマニュアルとサポートを提供します。',
    },
    {
      question: '作業できない案件はどうしたら？',
      answer: '作業できない案件は、無理に受注する必要はありません。案件通知時に難易度と作業内容が表示されるため、対応可能な案件のみを選択できます。',
    },
    {
      question: '自宅でもできますか？',
      answer: 'はい、可能です。キャンピングカーは移動可能なため、お客様の指定場所（自宅や駐車場など）で作業できます。ただし、作業環境によっては対応できない場合もあります。',
    },
    {
      question: '遠方からの依頼は？',
      answer: '遠方からの依頼も可能ですが、移動費や時間を考慮して見積もりを提出してください。お客様が移動費を負担する場合もあります。',
    },
    {
      question: '個人事業主でも登録できますか？',
      answer: 'はい、個人事業主の方も登録可能です。法人登録は不要です。',
    },
    {
      question: '手数料はいつ支払われますか？',
      answer: '売上一旦サポートセンターに入金してもらい、手数料を引いた金額を後日パートナー様へ送金致します。',
    },
  ];

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-900">
            よくある質問
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            よくあるご質問にお答えします
          </p>

          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-gray-50 rounded-lg p-6 border-l-4 border-green-500 hover:shadow-md transition-shadow"
              >
                <h3 className="text-lg font-bold text-gray-900 mb-2">Q. {faq.question}</h3>
                <p className="text-gray-700 leading-relaxed">A. {faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

