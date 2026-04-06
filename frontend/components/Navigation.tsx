'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';

export default function Navigation() {
  const pathname = usePathname();
  const [userRole, setUserRole] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setUserRole(localStorage.getItem('role'));
    }
  }, [pathname]);

  // 一般ユーザー向けページではナビゲーションを非表示
  const publicPages = ['/', '/chat', '/partner', '/lp-camper-repair', '/lp-partner-recruit', '/repair-advice', '/review'];
  const currentPath = pathname || '';
  const isPublicPage = publicPages.some((page) =>
    page === '/'
      ? currentPath === '/'
      : currentPath === page || currentPath.startsWith(`${page}/`)
  );

  // 一般ユーザー向けページではナビゲーションを表示しない
  if (isPublicPage) {
    return null;
  }

  // 管理者/工場向けページでのみナビゲーションを表示
  const navLinks = useMemo(() => {
    const base = [
      { href: '/', label: '🏠 ホーム', icon: '🏠' },
      { href: '/chat', label: '💬 チャット', icon: '💬' },
      { href: '/partner', label: '🔧 修理店紹介', icon: '🔧' },
      { href: '/factory', label: '🏭 工場ダッシュボード', icon: '🏭' },
    ];
    if (userRole === 'admin') {
      base.push({ href: '/admin', label: '⚙️ 管理者画面', icon: '⚙️' });
    }
    return base;
  }, [userRole]);

  return (
    <nav className="bg-white/95 backdrop-blur-sm rounded-lg shadow-md p-4 mb-6">
      <div className="flex flex-wrap gap-2 justify-center items-center">
        {navLinks.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                isActive
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
