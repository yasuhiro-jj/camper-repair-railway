import Link from "next/link";

type LatestPost = {
  title: string;
  excerpt: string;
  href: string;
  publishedAt: string;
};

// NOTE: 現在は仮データ。後日 WordPress / microCMS / Notion API と差し替え予定。
const latestPosts: LatestPost[] = [
  {
    title: "雨漏りチェックリスト23項目",
    excerpt: "ルーフベント・窓・サイドオーニングまわりを写真付きで解説。診断フォームと連動予定。",
    href: "/blog/trouble/rain-checklist",
    publishedAt: "2025-12-01",
  },
  {
    title: "電装アップグレードでやりがちな5つの失敗",
    excerpt: "配線容量・ヒューズ位置・放熱設計など、よくある失敗を事例ベースで整理。",
    href: "/blog/electrical/mistakes",
    publishedAt: "2025-11-22",
  },
  {
    title: "保険で修理費をカバーできるケース",
    excerpt: "保険対象になる破損・ならない破損の境界をまとめ、書類準備リストも紹介。",
    href: "/blog/risk-insurance/coverage",
    publishedAt: "2025-11-10",
  },
];

export default function LatestPosts() {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">最新記事（仮データ）</h2>
        <p className="text-sm text-slate-600">※ 近日中にCMS連携します。今は仮データで表示しています。</p>
      </div>
      <div className="space-y-4">
        {latestPosts.map((post) => (
          <article
            key={post.href}
            className="rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-slate-400"
          >
            <p className="text-xs text-slate-500">{post.publishedAt}</p>
            <h3 className="mt-1 text-lg font-semibold text-slate-900">{post.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{post.excerpt}</p>
            <Link href={post.href} className="mt-3 inline-flex text-sm font-semibold text-slate-900 underline-offset-2 hover:underline">
              記事を読む
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}




