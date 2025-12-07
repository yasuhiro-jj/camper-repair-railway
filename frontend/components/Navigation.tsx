'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
  const pathname = usePathname();

  // 一般ユーザー向けページではナビゲーションを非表示
  const publicPages = ['/', '/chat', '/partner', '/lp-camper-repair', '/lp-partner-recruit', '/repair-advice'];
  const isPublicPage = publicPages.includes(pathname || '');

  // 一般ユーザー向けページではナビゲーションを表示しない
  if (isPublicPage) {
    return null;
  }

  // 管理者/工場向けページでのみナビゲーションを表示
  const navLinks = [
    { href: '/', label: '🏠 ホーム', icon: '🏠' },
    { href: '/chat', label: '💬 チャット', icon: '💬' },
    { href: '/partner', label: '🔧 修理店紹介', icon: '🔧' },
    { href: '/factory', label: '🏭 工場ダッシュボード', icon: '🏭' },
    { href: '/admin', label: '⚙️ 管理者画面', icon: '⚙️' },
  ];

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

