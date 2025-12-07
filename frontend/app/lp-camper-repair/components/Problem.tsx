'use client';

export default function Problem() {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* セクションタイトル */}
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-slate-900">
            キャンピングカー修理の現状と課題
          </h2>

          {/* 課題リスト */}
          <div className="space-y-8">
            {/* 課題1 */}
            <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-r-lg">
              <div className="flex items-start gap-4">
                <div className="text-3xl">🚨</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">
                    修理工場が圧倒的に少ない
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    キャンピングカー業界は、一般の自動車修理とは異なる専門知識が必要なため、対応できる修理工場が全国的に不足しています。特に地方では、近くに修理できる工場がないという深刻な問題があります。
                  </p>
                </div>
              </div>
            </div>

            {/* 課題2 */}
            <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-r-lg">
              <div className="flex items-start gap-4">
                <div className="text-3xl">⚔️</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">
                    ビルダー同士の関係が悪く、紹介が回ってこない
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    業界内の競争が激しく、ビルダー同士が協力関係を築きにくい状況です。そのため、ユーザーは適切な修理工場を見つけることができず、困り果てています。
                  </p>
                </div>
              </div>
            </div>

            {/* 課題3 */}
            <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-r-lg">
              <div className="flex items-start gap-4">
                <div className="text-3xl">📍</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">
                    西日本は特に工場が不足
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    関東圏に比べて、西日本エリアの修理工場はさらに少なく、キャンピングカー所有者は遠方まで出向かなければならない状況が続いています。
                  </p>
                </div>
              </div>
            </div>

            {/* 課題4 */}
            <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-r-lg">
              <div className="flex items-start gap-4">
                <div className="text-3xl">❓</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">
                    どこへ相談すればいいかわからない
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    故障が発生しても、どこに相談すればいいのか、どの工場が対応できるのか、情報が不足しています。インターネットで検索しても、信頼できる情報が少ないのが現状です。
                  </p>
                </div>
              </div>
            </div>

            {/* 課題5 */}
            <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-r-lg">
              <div className="flex items-start gap-4">
                <div className="text-3xl">🔧</div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">
                    故障しても直せる工場が近くにない
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    緊急の故障が発生した場合でも、対応できる工場が遠方にしかないため、移動コストや時間がかかり、ユーザーの負担が大きくなっています。
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* 解決へのメッセージ */}
          <div className="mt-12 bg-slate-900 text-white p-8 rounded-lg text-center">
            <h3 className="text-2xl font-bold mb-4">
              これらの課題を解決するのが、私たちのプラットフォームです
            </h3>
            <p className="text-lg text-gray-200">
              AI診断と全国の修理工場ネットワークで、あなたの「困った」を最短で解決します
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

