import Link from "next/link";
import { categories } from "../lib/categories";

export default function CategoryGrid() {
  return (
    <section id="categories" className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">症状からカテゴリを選ぶ</h2>
          <p className="text-sm text-slate-600">10カテゴリはすべてRAGで連動。今後の追加も配列を増やすだけで反映できます。</p>
        </div>
        <p className="text-xs uppercase tracking-wide text-slate-500">すべての記事が診断・LINEと連携</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {categories.map((category) => (
          <Link
            key={category.slug}
            href={category.slug}
            className="rounded-2xl border border-slate-200 bg-white p-5 transition hover:shadow-lg"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-lg font-semibold text-slate-900">{category.name}</p>
                <p className="text-sm text-slate-500">{category.description}</p>
              </div>
              <span className="text-sm font-semibold text-yellow-500">記事へ</span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}




