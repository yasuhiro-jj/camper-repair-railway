import type { Metadata } from 'next';

const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';

export const metadata: Metadata = {
  title: '管理者画面',
  description: 'システム管理画面。データベース再構築、ファイル管理、システム情報、ビルダー管理機能を提供します。',
  robots: {
    index: false, // 管理者画面は検索エンジンにインデックスしない
    follow: false,
  },
};

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

