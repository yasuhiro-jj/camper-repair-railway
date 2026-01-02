'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Navigation from '@/components/Navigation';
import { reviewApi } from '@/lib/api';
import { useRouter } from 'next/navigation';

function ReviewPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [dealId, setDealId] = useState<string>('');
  const [partnerPageId, setPartnerPageId] = useState<string>('');
  const [customerName, setCustomerName] = useState<string>('');
  const [starRating, setStarRating] = useState<number>(0);
  const [hoveredRating, setHoveredRating] = useState<number>(0);
  const [comment, setComment] = useState<string>('');
  const [anonymous, setAnonymous] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const dealIdParam = searchParams.get('deal_id');
    const partnerPageIdParam = searchParams.get('partner_page_id');
    const customerNameParam = searchParams.get('customer_name');
    
    if (dealIdParam) setDealId(dealIdParam);
    if (partnerPageIdParam) setPartnerPageId(partnerPageIdParam);
    if (customerNameParam) setCustomerName(customerNameParam);
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!dealId || !partnerPageId || !customerName || starRating === 0) {
      setError('必須項目を入力してください');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await reviewApi.createReview(
        dealId,
        partnerPageId,
        customerName,
        starRating,
        comment,
        anonymous
      );
      
      alert('✅ 評価を送信しました。ありがとうございました！');
      router.push('/partner');
    } catch (err: any) {
      setError(err.message || '評価の送信に失敗しました');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStars = (rating: number, interactive: boolean = false) => {
    return (
      <div className="flex items-center gap-2">
        {[1, 2, 3, 4, 5].map((star) => {
          const displayRating = interactive ? (hoveredRating || rating) : rating;
          const isFilled = star <= displayRating;
          
          return (
            <button
              key={star}
              type="button"
              onClick={() => interactive && setStarRating(star)}
              onMouseEnter={() => interactive && setHoveredRating(star)}
              onMouseLeave={() => interactive && setHoveredRating(0)}
              disabled={!interactive || isSubmitting}
              className={`text-4xl transition-all ${
                isFilled ? 'text-yellow-400' : 'text-gray-300'
              } ${interactive ? 'hover:scale-110 cursor-pointer' : ''} ${
                !interactive || isSubmitting ? 'cursor-default' : ''
              }`}
            >
              ★
            </button>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-2xl mx-auto">
        <Navigation />

        <div className="bg-white rounded-lg shadow-sm p-8 mt-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ⭐ 修理店の評価
          </h1>
          <p className="text-gray-600 mb-6">
            修理が完了しましたら、ぜひご評価をお願いいたします。
          </p>

          {error && (
            <div className="bg-red-100 text-red-800 p-4 rounded-lg mb-6 border border-red-300">
              ❌ {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 商談ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                商談ID <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={dealId}
                onChange={(e) => setDealId(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例: DEAL-20241103-001"
              />
            </div>

            {/* パートナー工場ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                パートナー工場ID <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={partnerPageId}
                onChange={(e) => setPartnerPageId(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* お客様名 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                お名前 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例: 田中太郎"
              />
            </div>

            {/* 星評価 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                星評価 <span className="text-red-500">*</span>
              </label>
              <div className="mb-2">
                {renderStars(starRating, true)}
              </div>
              <p className="text-sm text-gray-600">
                {starRating > 0 ? `${starRating}つ星を選択中` : '星をクリックして評価してください'}
              </p>
            </div>

            {/* コメント */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                コメント
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="修理店へのコメントをご記入ください（任意）"
              />
            </div>

            {/* 匿名希望 */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="anonymous"
                checked={anonymous}
                onChange={(e) => setAnonymous(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="anonymous" className="ml-2 text-sm text-gray-700">
                匿名で投稿する
              </label>
            </div>

            {/* 送信ボタン */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={isSubmitting || starRating === 0}
                className="flex-1 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isSubmitting ? '送信中...' : '評価を送信'}
              </button>
              <button
                type="button"
                onClick={() => router.push('/partner')}
                className="px-6 py-3 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition-colors"
              >
                キャンセル
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function ReviewPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    }>
      <ReviewPageContent />
    </Suspense>
  );
}





















