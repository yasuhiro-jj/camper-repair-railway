'use client';

import { useState } from 'react';
import Navigation from '@/components/Navigation';
import { customerNoteApi } from '@/lib/api';

export default function CustomerNotePage() {
  const [dealId, setDealId] = useState('');
  const [note, setNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!dealId.trim() || !note.trim()) {
      setError('商談IDとメッセージを入力してください');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSuccess(false);

    try {
      const result = await customerNoteApi.addNote(dealId.trim(), note.trim());
      if (result.success) {
        setSuccess(true);
        setNote('');
        setTimeout(() => {
          setSuccess(false);
          setDealId('');
        }, 5000);
      } else {
        setError(result.error || 'メッセージの送信に失敗しました');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'メッセージの送信に失敗しました');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-2xl mx-auto">
        {/* ナビゲーション */}
        <Navigation />

        {/* ヘッダー */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            💬 修理店にメッセージを送る
          </h1>
          <p className="text-gray-600">
            スケジュール調整や追加のご質問がある場合は、こちらからメッセージを送信できます。
          </p>
        </div>

        {/* フォーム */}
        {success ? (
          <div className="bg-green-100 text-green-800 p-6 rounded-lg border border-green-300">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">✅</span>
              <h3 className="text-lg font-bold">メッセージを送信しました</h3>
            </div>
            <p className="text-sm">修理店より連絡がありますので、しばらくお待ちください。</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  商談ID <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={dealId}
                  onChange={(e) => setDealId(e.target.value)}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                  placeholder="例: DEAL-20241103-001"
                />
                <p className="text-xs text-gray-500 mt-1">
                  ※ 問い合わせフォーム送信時に表示された商談IDを入力してください
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  メッセージ <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  required
                  rows={6}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="例: 来週の月曜日から車を持って行けます。"
                />
              </div>

              {error && (
                <div className="bg-red-100 text-red-800 p-4 rounded-lg border border-red-300">
                  ❌ {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting || !dealId.trim() || !note.trim()}
                className="w-full px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
              >
                {isSubmitting ? '送信中...' : '📤 メッセージを送信'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
























