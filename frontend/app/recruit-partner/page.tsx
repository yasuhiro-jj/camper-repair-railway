'use client';

import { useState } from 'react';
import Navigation from '@/components/Navigation';

export default function RecruitPartnerPage() {
  const [formData, setFormData] = useState({
    shop_name: '',
    contact_name: '',
    phone: '',
    email: '',
    prefecture: '',
    specialty: '',
    message: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // TODO: バックエンドAPIに送信
    // ここではフォーム送信のロジックを実装
    setTimeout(() => {
      setSuccess(true);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      
      {/* ヒーローセクション */}
      <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-purple-800 text-white py-20">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            キャンピングカー修理の協力会社を募集しています
          </h1>
          <p className="text-xl mb-8 text-blue-100">
            AIを活用した修理プラットフォームで、新しい顧客獲得のチャンスを
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-4">
              <div className="text-3xl font-bold">500+</div>
              <div className="text-sm">月間問い合わせ数</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-4">
              <div className="text-3xl font-bold">100+</div>
              <div className="text-sm">登録修理店</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg px-6 py-4">
              <div className="text-3xl font-bold">24/7</div>
              <div className="text-sm">AIサポート</div>
            </div>
          </div>
        </div>
      </section>

      {/* メリットセクション */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            協力会社になるメリット
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-lg shadow-lg">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-xl font-bold mb-3">新規顧客の獲得</h3>
              <p className="text-gray-600">
                AIチャットボットを通じて、修理を必要とする顧客を自動的に紹介。月間500件以上の問い合わせから、あなたの専門分野に合った案件をマッチングします。
              </p>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-lg">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-bold mb-3">AIによる事前診断</h3>
              <p className="text-gray-600">
                顧客の症状をAIが事前に診断し、適切な修理店に紹介。無駄な問い合わせを減らし、成約率の高い案件のみをご紹介します。
              </p>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-lg">
              <div className="text-4xl mb-4">💰</div>
              <h3 className="text-xl font-bold mb-3">手数料システム</h3>
              <p className="text-gray-600">
                成約時にのみ手数料が発生する成功報酬型。初期費用や月額費用は一切かかりません。あなたの実績に応じて収益が増えます。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 応募フォームセクション */}
      <section className="py-16 bg-white">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-8">
            協力会社登録フォーム
          </h2>
          
          {success ? (
            <div className="bg-green-100 border border-green-400 text-green-700 px-6 py-8 rounded-lg text-center">
              <div className="text-4xl mb-4">✅</div>
              <h3 className="text-xl font-bold mb-2">お申し込みありがとうございます</h3>
              <p>担当者より3営業日以内にご連絡いたします。</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6 bg-gray-50 p-8 rounded-lg shadow-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  修理店名 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.shop_name}
                  onChange={(e) => setFormData({ ...formData, shop_name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="例: 〇〇自動車整備工場"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  担当者名 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.contact_name}
                  onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="例: 山田太郎"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    電話番号 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="例: 090-1234-5678"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    メールアドレス <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="例: example@email.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  所在地（都道府県） <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={formData.prefecture}
                  onChange={(e) => setFormData({ ...formData, prefecture: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">選択してください</option>
                  <option value="北海道">北海道</option>
                  <option value="青森県">青森県</option>
                  {/* 他の都道府県も追加 */}
                  <option value="岡山県">岡山県</option>
                  {/* ... */}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  専門分野 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.specialty}
                  onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="例: エアコン、バッテリー、エンジン整備"
                />
                <p className="text-sm text-gray-500 mt-1">
                  複数の専門分野がある場合は、カンマ区切りで入力してください
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  メッセージ（任意）
                </label>
                <textarea
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  rows={5}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="ご質問やご要望がございましたら、こちらにご記入ください"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-4 rounded-lg font-bold text-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '送信中...' : '📧 協力会社登録を申し込む'}
              </button>
            </form>
          )}
        </div>
      </section>

      {/* FAQセクション */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            よくある質問
          </h2>
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-xl font-bold mb-2">Q. 登録費用はかかりますか？</h3>
              <p className="text-gray-600">
                A. いいえ、登録費用や月額費用は一切かかりません。成約時にのみ手数料が発生する成功報酬型です。
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-xl font-bold mb-2">Q. どのような修理店が登録できますか？</h3>
              <p className="text-gray-600">
                A. キャンピングカーの修理実績がある修理店であれば、個人事業主から法人まで幅広く登録可能です。
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-xl font-bold mb-2">Q. 紹介される案件の質はどうですか？</h3>
              <p className="text-gray-600">
                A. AIによる事前診断により、適切な修理店にマッチングされます。無駄な問い合わせを減らし、成約率の高い案件のみをご紹介します。
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-xl font-bold mb-2">Q. 手数料はいくらですか？</h3>
              <p className="text-gray-600">
                A. 手数料率は修理内容や金額によって異なります。詳細は登録後にご案内いたします。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTAセクション */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            まずはお気軽にお問い合わせください
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            ご不明な点がございましたら、お気軽にお問い合わせください
          </p>
          <a
            href="mailto:info@example.com"
            className="inline-block bg-white text-blue-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors"
          >
            📧 お問い合わせ
          </a>
        </div>
      </section>
    </div>
  );
}
