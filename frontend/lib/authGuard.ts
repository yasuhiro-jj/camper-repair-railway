/**
 * 認証ガード（Protected Route）
 * 認証が必要なページで使用するフック
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from './api';

export function useAuthGuard() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (typeof window === 'undefined') {
        setIsLoading(false);
        return;
      }

      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        router.push('/factory/login');
        return;
      }

      try {
        // トークンの有効性を確認
        await authApi.getCurrentUser();
        setIsAuthenticated(true);
      } catch (error) {
        // トークンが無効な場合はログインページにリダイレクト
        localStorage.removeItem('auth_token');
        localStorage.removeItem('factory_id');
        localStorage.removeItem('factory_name');
        localStorage.removeItem('role');
        router.push('/factory/login');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  return { isAuthenticated, isLoading };
}
