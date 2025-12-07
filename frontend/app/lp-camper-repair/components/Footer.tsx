'use client';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-white py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            {/* 会社情報 */}
            <div>
              <h3 className="text-xl font-bold mb-4">キャンピングカー修理工場マッチング</h3>
              <p className="text-gray-300 text-sm leading-relaxed">
                全国のキャンピングカー所有者と修理工場を繋ぐプラットフォーム。AI診断で最適なマッチングを実現します。
              </p>
            </div>

            {/* リンク */}
            <div>
              <h4 className="text-lg font-bold mb-4">リンク</h4>
              <ul className="space-y-2">
                <li>
                  <a href="/chat" className="text-gray-300 hover:text-yellow-400 transition-colors">
                    無料診断
                  </a>
                </li>
                <li>
                  <a href="#for-partners" className="text-gray-300 hover:text-yellow-400 transition-colors">
                    修理工場登録
                  </a>
                </li>
                <li>
                  <a href="#cta" className="text-gray-300 hover:text-yellow-400 transition-colors">
                    お問い合わせ
                  </a>
                </li>
              </ul>
            </div>

            {/* 連絡先 */}
            <div>
              <h4 className="text-lg font-bold mb-4">お問い合わせ</h4>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>📞 電話: <a href="tel:086-206-6622" className="hover:text-yellow-400">086-206-6622</a></li>
                <li>📧 メール: <a href="mailto:info@example.com" className="hover:text-yellow-400">info@example.com</a></li>
                <li>📍 所在地: 岡山県</li>
              </ul>
            </div>
          </div>

          {/* コピーライト */}
          <div className="border-t border-white/20 pt-8 text-center text-gray-400 text-sm">
            <p>&copy; 2025 キャンピングカー修理工場マッチング. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}

