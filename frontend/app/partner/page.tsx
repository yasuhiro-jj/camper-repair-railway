'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Navigation from '@/components/Navigation';
import ShopList from '@/components/Partner/ShopList';
import InquiryForm from '@/components/Partner/InquiryForm';
import { PartnerShop } from '@/lib/api';

function PartnerPageContent() {
  const searchParams = useSearchParams();
  const [selectedShop, setSelectedShop] = useState<PartnerShop | null>(null);
  const [showInquiryForm, setShowInquiryForm] = useState(false);
  const [filterPrefecture, setFilterPrefecture] = useState<string>('');
  const [filterSpecialty, setFilterSpecialty] = useState<string>('');
  const [defaultSymptom, setDefaultSymptom] = useState<string>('');

  // URLパラメータから初期値を設定
  useEffect(() => {
    const category = searchParams.get('category');
    const symptom = searchParams.get('symptom');
    
    if (category) {
      setFilterSpecialty(category);
    }
    
    if (symptom) {
      setDefaultSymptom(symptom);
    }
  }, [searchParams]);

  const handleShopSelect = (shop: PartnerShop) => {
    setSelectedShop(shop);
    setShowInquiryForm(true);
  };

  const handleInquirySuccess = (dealId: string) => {
    alert(`✅ 問い合わせを受け付けました（商談ID: ${dealId}）`);
    setShowInquiryForm(false);
    setSelectedShop(null);
  };

  const handleCancel = () => {
    setShowInquiryForm(false);
    setSelectedShop(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* ナビゲーション */}
        <Navigation />

        {/* ヘッダー */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🔧 パートナー修理店紹介
              </h1>
              <p className="text-gray-600">
                お客様に最適な修理店をご紹介します
              </p>
            </div>
            {!showInquiryForm && (
              <button
                onClick={() => {
                  setShowInquiryForm(true);
                  setSelectedShop({
                    shop_id: 'demo',
                    name: 'デモ修理店',
                    page_id: 'demo-page-id',
                  } as PartnerShop);
                }}
                className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-semibold"
              >
                📝 お問い合わせフォームを見る
              </button>
            )}
          </div>
        </div>

        {/* フィルタ */}
        {!showInquiryForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">検索フィルタ</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  都道府県
                </label>
                <input
                  type="text"
                  value={filterPrefecture}
                  onChange={(e) => setFilterPrefecture(e.target.value)}
                  placeholder="例: 東京都、大阪府"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  専門分野
                </label>
                <input
                  type="text"
                  value={filterSpecialty}
                  onChange={(e) => setFilterSpecialty(e.target.value)}
                  placeholder="例: エアコン、バッテリー"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                />
              </div>
            </div>
          </div>
        )}

        {/* 問い合わせフォーム */}
        {showInquiryForm && selectedShop && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                問い合わせフォーム
              </h2>
              {selectedShop.shop_id !== 'demo' ? (
                <p className="text-sm text-gray-600 mb-4">
                  選択された修理店: <span className="font-semibold">{selectedShop.name}</span>
                </p>
              ) : (
                <p className="text-sm text-gray-600 mb-4">
                  <span className="font-semibold">※ デモ表示モード</span> - 実際の修理店を選択するには、修理店一覧から選択してください。
                </p>
              )}
            </div>
            <InquiryForm
              defaultCategory={filterSpecialty}
              defaultDetail={defaultSymptom}
              defaultPrefecture={filterPrefecture}
              partnerPageId={selectedShop.page_id}
              partnerShop={selectedShop}
              onSuccess={handleInquirySuccess}
              onCancel={handleCancel}
            />
          </div>
        )}

        {/* パートナー修理店一覧 */}
        {!showInquiryForm && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              パートナー修理店一覧
            </h2>
            <ShopList
              prefecture={filterPrefecture || undefined}
              specialty={filterSpecialty || undefined}
              onShopSelect={handleShopSelect}
              showSelectButton={true}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default function PartnerPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600">読み込み中...</p>
      </div>
    </div>}>
      <PartnerPageContent />
    </Suspense>
  );
}

