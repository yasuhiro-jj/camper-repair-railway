import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '工場ダッシュボード',
  description: '工場向けの案件管理ダッシュボード。修理案件のステータス管理、コメント追加、フィルタリング機能を提供します。',
  robots: {
    index: false, // 工場ダッシュボードは検索エンジンにインデックスしない
    follow: false,
  },
};

export default function FactoryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
