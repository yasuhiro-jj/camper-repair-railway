'use client';

export default function Conditions() {
  const conditions = [
    {
      icon: '✅',
      title: 'キャンピングカー専門でなくてOK',
      description: '専門知識がなくても、基本的な技術があれば対応可能です。',
    },
    {
      icon: '🔧',
      title: '普通の工具があればOK',
      description: '特別な工具は必要ありません。一般的な工具で作業できます。',
    },
    {
      icon: '👤',
      title: '個人事業主可',
      description: '法人だけでなく、個人事業主の方も登録可能です。',
    },
    {
      icon: '💝',
      title: '作業スピードより「誠実対応」を重視',
      description: 'スピードよりも、丁寧で誠実な対応を重視しています。',
    },
    {
      icon: '⚠️',
      title: 'ルール遵守について',
      description: '悪質なパートナー様、ルールを守らないパートナー様は解除させていただくことがございますので予めご了承ください。',
    },
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-900">
            パートナー条件
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            ハードルは低く、誰でも参画できる環境を整えています
          </p>

          <div className="grid md:grid-cols-2 gap-6">
            {conditions.map((condition, index) => (
              <div
                key={index}
                className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start gap-4">
                  <div className="text-4xl">{condition.icon}</div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{condition.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{condition.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

