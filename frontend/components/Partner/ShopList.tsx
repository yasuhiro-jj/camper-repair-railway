'use client';

import { useState, useEffect } from 'react';
import { partnerShopApi, PartnerShop } from '@/lib/api';
import ShopCard from './ShopCard';

interface ShopListProps {
  prefecture?: string;
  specialty?: string;
  onShopSelect?: (shop: PartnerShop) => void;
  showSelectButton?: boolean;
}

export default function ShopList({
  prefecture,
  specialty,
  onShopSelect,
  showSelectButton = false,
}: ShopListProps) {
  const [shops, setShops] = useState<PartnerShop[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadShops();
  }, [prefecture, specialty]);

  const loadShops = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // 都道府県フィルタは部分一致でフロントエンド側でフィルタリング
      // バックエンドには空で送信（全件取得）
      const shopList = await partnerShopApi.getShops(
        'アクティブ', // アクティブな店舗のみ
        undefined, // 都道府県はフロントエンドでフィルタリング
        specialty
      );
      
      // フロントエンド側で都道府県の部分一致フィルタリング
      let filteredShops = shopList;
      if (prefecture && prefecture.trim()) {
        const prefectureLower = prefecture.toLowerCase().trim();
        filteredShops = shopList.filter(shop => {
          const shopPrefecture = (shop.prefecture || '').toLowerCase();
          return shopPrefecture.includes(prefectureLower);
        });
      }
      
      setShops(filteredShops);
    } catch (err: any) {
      console.error('パートナー修理店一覧取得エラー:', err);
      
      // より詳細なエラーメッセージを表示
      let errorMessage = 'パートナー修理店の取得に失敗しました';
      
      if (err.code === 'ECONNREFUSED' || err.message?.includes('Network Error')) {
        errorMessage = 'バックエンドサーバーに接続できません。サーバーが起動しているか確認してください。';
      } else if (err.response?.status === 404) {
        errorMessage = 'APIエンドポイントが見つかりません。';
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <p className="mt-2 text-gray-600">読み込み中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 text-red-800 p-4 rounded-lg border border-red-300">
        ❌ {error}
      </div>
    );
  }

  if (shops.length === 0) {
    return (
      <div className="text-center py-8 text-gray-600">
        パートナー修理店が見つかりませんでした
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {shops.map((shop) => (
        <ShopCard
          key={shop.shop_id || shop.page_id}
          shop={shop}
          onSelect={onShopSelect}
          showSelectButton={showSelectButton}
        />
      ))}
    </div>
  );
}

