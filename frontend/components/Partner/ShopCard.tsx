'use client';

import React from 'react';
import { PartnerShop } from '@/lib/api';

interface ShopCardProps {
  shop: PartnerShop;
  onSelect?: (shop: PartnerShop) => void;
  showSelectButton?: boolean;
}

const ShopCard: React.FC<ShopCardProps> = ({ shop, onSelect, showSelectButton = false }) => {
  // 星評価の表示
  const renderStars = (rating: number) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    return (
      <div className="flex items-center gap-1">
        {Array.from({ length: fullStars }).map((_, i) => (
          <span key={`full-${i}`} className="text-yellow-400 text-lg">★</span>
        ))}
        {hasHalfStar && <span className="text-yellow-400 text-lg">☆</span>}
        {Array.from({ length: emptyStars }).map((_, i) => (
          <span key={`empty-${i}`} className="text-gray-300 text-lg">★</span>
        ))}
        <span className="ml-2 text-sm text-gray-600">
          {rating > 0 ? rating.toFixed(1) : '評価なし'} ({shop.review_count || 0}件)
        </span>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-2">{shop.name}</h3>
          <p className="text-sm text-gray-600 mb-1">
            📍 {shop.prefecture} {shop.address}
          </p>
          <p className="text-sm text-gray-600 mb-1">
            📞 {shop.phone}
          </p>
          {shop.business_hours && (
            <p className="text-sm text-gray-600 mb-1">
              🕐 {shop.business_hours}
            </p>
          )}
        </div>
      </div>

      {/* 評価表示 */}
      <div className="mb-4">
        {renderStars(shop.avg_rating || 0)}
      </div>

      {/* 専門分野 */}
      {shop.specialties && (
        <div className="mb-4">
          <p className="text-sm font-semibold text-gray-700 mb-2">専門分野:</p>
          <div className="flex flex-wrap gap-2">
            {shop.specialties.map((specialty, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 rounded-md text-xs"
              >
                {specialty}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 統計情報 */}
      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div className="bg-gray-50 p-2 rounded">
          <p className="text-gray-600">修理回数</p>
          <p className="text-lg font-bold text-gray-900">{shop.repair_count || 0}件</p>
        </div>
        <div className="bg-gray-50 p-2 rounded">
          <p className="text-gray-600">修理金額合計</p>
          <p className="text-lg font-bold text-gray-900">
            {shop.total_repair_amount ? `${(shop.total_repair_amount / 10000).toFixed(0)}万円` : '0円'}
          </p>
        </div>
      </div>

      {/* 初診断料 */}
      {shop.initial_diagnosis_fee && (
        <p className="text-sm text-gray-600 mb-4">
          初診断料: <span className="font-semibold">{shop.initial_diagnosis_fee.toLocaleString()}円</span>
        </p>
      )}

      {/* 選択ボタン */}
      {showSelectButton && onSelect && (
        <button
          onClick={() => onSelect(shop)}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-semibold"
        >
          この修理店に問い合わせる
        </button>
      )}
    </div>
  );
};

export default ShopCard;
