import Link from "next/link";

type FeaturedPost = {
  title: string;
  description: string;
  href: string;
  category: string;
};

const featuredPosts: FeaturedPost[] = [
  {
    title: "後付けエアコンの選び方",
    description: "冷却能力・電力計算・室外機設置位置まで、失敗しない工事のチェックポイントを整理。",
    href: "/blog/air-conditioner1",
    category: "エアコン",
  },
  {
    title: "FFヒーターがつかない原因",
    description: "燃焼系・電装系・吸排気の切り分けを手順化。3分診断への動線も設置済み。",
    href: "/blog/ff-heater",
    category: "FFヒーター",
  },
  {
    title: "サブバッテリー容量の決め方",
    description: "使用家電・滞在日数・充電方法から最適容量を算出。見積もり前に前提条件を揃えます。",
    href: "/blog/sub-battery",
    category: "サブバッテリー",
  },
  {
    title: "インバーター容量計算",
    description: "同時使用電力と起動電流を考慮した計算式を公開。診断アプリへの導線をセット。",
    href: "/blog/inverter",
    category: "電装",
  },
];

export default function FeaturedPosts() {
  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-yellow-500">Search Consoleで強い記事</p>
          <h2 className="text-2xl font-semibold text-slate-900">おすすめ記事（固定表示）</h2>
        </div>
        <p className="text-xs text-slate-500">※ 診断・LINE相談に直結する記事のみを厳選</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {featuredPosts.map((post) => (
          <article
            key={post.href}
            className="rounded-2xl border border-slate-200 bg-white p-6 transition hover:border-yellow-400 hover:shadow-lg"
          >
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{post.category}</p>
            <h3 className="mt-2 text-xl font-semibold text-slate-900">{post.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{post.description}</p>
            <div className="mt-4">
              <Link href={post.href} className="text-sm font-semibold text-yellow-600 hover:underline">
                記事を読む
              </Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}




