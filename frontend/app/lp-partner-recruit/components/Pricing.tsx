'use client';

export default function Pricing() {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-900">
            料金モデル
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            シンプルでわかりやすい料金体系です
          </p>

          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-8 md:p-12 border-2 border-green-200">
            <div className="text-center mb-8">
              <div className="text-5xl font-bold text-green-600 mb-2">登録費：無料</div>
              <p className="text-gray-700 text-lg">初期費用や月額費用は一切かかりません</p>
            </div>

            <div className="bg-white rounded-lg p-8 mb-6">
              <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">
                手数料について
              </h3>
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="text-green-500 text-2xl">💰</div>
                  <div>
                    <p className="text-lg font-semibold text-gray-900 mb-2">
                      修理代金の30%を紹介料として当社が頂きます
                    </p>
                    <p className="text-gray-600">
                      売上一旦サポートセンターに入金してもらい、手数料を引いた金額を後日パートナー様へ送金致します
                    </p>
                  </div>
                </div>
                <div className="mt-6 p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-700">
                    <strong>例：</strong>修理代金が10万円の場合、サポートセンターに10万円が入金され、手数料3万円（修理代金の30%に相当）を差し引いた7万円を後日パートナー様へ送金いたします。
                  </p>
                </div>
              </div>
            </div>

            <div className="text-center">
              <p className="text-gray-600 mb-4">
                手数料またはその他のことに関する詳細はメールもしくはお電話にてお尋ねください
              </p>
              <div className="flex flex-col gap-4 justify-center items-center">
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                  <a
                    href="#form"
                    className="inline-block bg-green-600 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-700 transition-colors shadow-lg"
                  >
                    📝 無料で登録する
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
      </div>
    </section>
  );
}

