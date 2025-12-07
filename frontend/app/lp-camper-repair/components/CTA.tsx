'use client';

import { useState } from 'react';

export default function CTA() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    region: '',
    issue: '',
    type: 'user', // 'user' or 'partner'
    message: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/inquiry', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('送信に失敗しました');
      }

      setSuccess(true);
      setFormData({
        name: '',
        email: '',
        phone: '',
        region: '',
        issue: '',
        type: 'user',
        message: '',
      });
    } catch (err) {
      setError('送信に失敗しました。もう一度お試しください。');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="cta" className="py-20 bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* セクションタイトル */}
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            お問い合わせ・登録
          </h2>
          <p className="text-center text-gray-300 mb-12 text-lg">
            無料診断や修理工場登録はこちらから
          </p>

          {/* クイックアクションボタン */}
          <div className="grid md:grid-cols-2 gap-4 mb-12">
            <a
              href="/chat"
              className="bg-yellow-400 text-slate-900 px-6 py-4 rounded-lg font-bold text-center hover:bg-yellow-300 transition-colors shadow-lg"
            >
              💬 LINEで無料診断
            </a>
            <a
              href="tel:086-206-6622"
              className="bg-white/10 backdrop-blur-sm border-2 border-white/30 text-white px-6 py-4 rounded-lg font-bold text-center hover:bg-white/20 transition-colors shadow-lg"
            >
              📞 お問い合わせ
            </a>
          </div>

          {/* フォーム */}
          {success ? (
            <div className="bg-green-500 text-white p-8 rounded-lg text-center">
              <div className="text-5xl mb-4">✅</div>
              <h3 className="text-2xl font-bold mb-2">送信完了しました</h3>
              <p>担当者より3営業日以内にご連絡いたします。</p>
            </div>
          ) : (
            <form id="form" onSubmit={handleSubmit} className="bg-white text-slate-900 rounded-lg p-8 shadow-xl">
              {/* 依頼種別 - デフォルトでユーザー（修理依頼）に設定 */}
              <input
                type="hidden"
                value="user"
              />

              {/* 名前 */}
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  お名前 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="例: 山田太郎"
                />
              </div>

              {/* メール */}
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  メールアドレス <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="例: example@email.com"
                />
              </div>

              {/* 電話番号 */}
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  電話番号 <span className="text-red-500">*</span>
                </label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="例: 090-1234-5678"
                />
              </div>

              {/* 地域 */}
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  地域（都道府県） <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.region}
                  onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="例: 岡山県"
                />
              </div>

              {/* 故障内容（ユーザーの場合）または事業内容（パートナーの場合） */}
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  {formData.type === 'user' ? '故障内容' : '事業内容'} <span className="text-red-500">*</span>
                </label>
                <textarea
                  required
                  value={formData.issue}
                  onChange={(e) => setFormData({ ...formData, issue: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder={formData.type === 'user' ? '例: エアコンが効かない、バッテリーが上がらない' : '例: 自動車整備工場、大工、電気工事'}
                />
              </div>

              {/* メッセージ */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">メッセージ（任意）</label>
                <textarea
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  placeholder="ご質問やご要望がございましたら、こちらにご記入ください"
                />
              </div>

              {/* エラーメッセージ */}
              {error && (
                <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              {/* 送信ボタン */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-yellow-400 text-slate-900 py-4 rounded-lg font-bold text-lg hover:bg-yellow-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                {isLoading ? '送信中...' : '📧 送信する'}
              </button>
            </form>
          )}
        </div>
      </div>
    </section>
  );
}

