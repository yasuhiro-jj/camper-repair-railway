'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authApi } from '@/lib/api';

export default function FactoryLogin() {
  const router = useRouter();
  const [loginId, setLoginId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await authApi.login(loginId, password);

      // トークンをlocalStorageに保存
      localStorage.setItem('auth_token', response.token);
      localStorage.setItem('factory_id', response.factory_id);
      localStorage.setItem('factory_name', response.factory_name);
      localStorage.setItem('role', response.role);
      
      // ダッシュボードにリダイレクト
      router.push('/factory');
    } catch (err: any) {
      if (err.message) {
        setError(err.message);
      } else if (err.response?.status === 401) {
        setError('ログインIDまたはパスワードが正しくありません');
      } else if (err.response?.status === 403) {
        setError('このアカウントは無効化されています');
      } else {
        setError('ログインに失敗しました。もう一度お試しください。');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🔧 工場ログイン</h1>
          <p className="text-gray-600 mt-2">キャンピングカー修理システム</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label htmlFor="loginId" className="block text-sm font-medium text-gray-700 mb-2">
              ログインID
            </label>
            <input
              type="text"
              id="loginId"
              value={loginId}
              onChange={(e) => setLoginId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="factory001"
              required
            />
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              パスワード
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
              required
            />
            <div className="mt-2 text-right">
              <Link
                href="/factory/forgot-password"
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                パスワードをお忘れですか？
              </Link>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'ログイン中...' : 'ログイン'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>ログインIDをお持ちでない場合は、管理者にお問い合わせください。</p>
        </div>
      </div>
    </div>
  );
}
