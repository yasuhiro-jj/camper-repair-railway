'use client';

import { useState } from 'react';
import Link from 'next/link';
import { authApi } from '@/lib/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setIsLoading(true);

    try {
      await authApi.requestPasswordReset(email);
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'メールの送信に失敗しました。もう一度お試しください。');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🔑 パスワードリセット</h1>
          <p className="text-gray-600 mt-2">登録済みのメールアドレスを入力してください</p>
        </div>

        {success ? (
          <div className="space-y-6">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 text-sm">
                パスワードリセット用のメールを送信しました。
                <br />
                登録されたメールアドレスに送信しています。メールをご確認ください。
              </p>
            </div>
            <p className="text-sm text-gray-600">
              メールが届かない場合は、迷惑メールフォルダをご確認ください。
              リンクの有効期限は60分です。
            </p>
            <Link
              href="/factory/login"
              className="block w-full text-center py-2 px-4 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors"
            >
              ログインページに戻る
            </Link>
          </div>
        ) : (
          <>
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  メールアドレス
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="example@example.com"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? '送信中...' : 'リセットメールを送信'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <Link
                href="/factory/login"
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                ← ログインページに戻る
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
