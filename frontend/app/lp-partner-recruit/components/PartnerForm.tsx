'use client';

import { useState } from 'react';

export default function PartnerForm() {
  const [formData, setFormData] = useState({
    name: '',
    company_name: '',
    phone: '',
    email: '',
    area: '',
    skills: '',
    equipment: '',
    experience: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('/api/partner-recruit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('送信に失敗しました');
      }

      const result = await response.json();
      setSuccess(true);
      
      // フォームをリセット
      setFormData({
        name: '',
        company_name: '',
        phone: '',
        email: '',
        area: '',
        skills: '',
        equipment: '',
        experience: '',
      });
    } catch (error) {
      alert('送信に失敗しました。もう一度お試しください。');
      console.error('送信エラー:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="form" className="py-20 bg-gradient-to-br from-green-600 to-emerald-700 text-white">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            パートナー登録フォーム
          </h2>
          <p className="text-center text-green-100 mb-12 text-lg">
            無料で登録できます。まずはお気軽にお申し込みください。
          </p>

          {success ? (
            <div className="bg-white text-green-700 p-8 rounded-lg text-center shadow-xl">
              <div className="text-5xl mb-4">✅</div>
              <h3 className="text-2xl font-bold mb-2">お申し込みありがとうございます</h3>
              <p>担当者より3営業日以内にご連絡いたします。</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="bg-white text-gray-900 rounded-lg p-8 shadow-xl">
              <div className="space-y-6">
                {/* 名前 */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    お名前 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="例: 山田太郎"
                  />
                </div>

                {/* 会社名 */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    会社名（個人事業主の場合は個人名） <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.company_name}
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="例: 〇〇自動車整備工場"
                  />
                </div>

                {/* 電話番号 */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    電話番号 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="例: 090-1234-5678"
                  />
                </div>

                {/* メールアドレス */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    メールアドレス <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="例: example@email.com"
                  />
                </div>

                {/* エリア */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    対応エリア（都道府県） <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.area}
                    onChange={(e) => setFormData({ ...formData, area: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="例: 岡山県、広島県"
                  />
                </div>

                {/* できる作業 */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    できる作業 <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    required
                    value={formData.skills}
                    onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="例: エアコン修理、バッテリー交換、水回り工事、電装工事"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    複数の作業が可能な場合は、カンマ区切りで入力してください
                  </p>
                </div>

                {/* 設備・経験の有無 */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    設備・経験の有無
                  </label>
                  <textarea
                    value={formData.equipment}
                    onChange={(e) => setFormData({ ...formData, equipment: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="例: 基本的な工具一式あり、住宅リフォーム経験10年"
                  />
                </div>

                {/* 送信ボタン */}
                <div className="space-y-4">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-green-600 text-white py-4 rounded-lg font-bold text-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                  >
                    {isLoading ? '送信中...' : '📧 無料でパートナー登録する'}
                  </button>
                  <a
                    href="tel:086-206-6622"
                    className="block w-full bg-white text-green-700 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 text-center border-2 border-green-700"
                  >
                    📞 まずは話を聞いてみる
                  </a>
                  <a
                    href="https://camper-repair.net/contact/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full bg-white text-green-700 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 text-center border-2 border-green-700"
                  >
                    📧 メールで聞いてみる
                  </a>
                </div>
              </div>
            </form>
          )}
        </div>
      </div>
    </section>
  );
}

