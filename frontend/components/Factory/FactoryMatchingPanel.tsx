'use client';

import { useState } from 'react';
import { factoryMatchingApi, type MatchedFactory } from '@/lib/api';

/**
 * 工場ダッシュボード用：提携工場の候補検索（折りたたみ）。
 * 日常の案件対応とは別用途のため、デフォルトは閉じた状態。
 */
export default function FactoryMatchingPanel() {
  const [open, setOpen] = useState(false);
  const [category, setCategory] = useState('');
  const [userMessage, setUserMessage] = useState('');
  const [prefecture, setPrefecture] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<MatchedFactory[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!userMessage.trim() && !category.trim()) {
      setError('カテゴリまたは症状・メッセージのどちらかを入力してください');
      return;
    }
    setLoading(true);
    setError(null);
    setResults([]);
    setHasSearched(false);
    try {
      const list = await factoryMatchingApi.matchFactories(
        {
          category: category.trim(),
          user_message: userMessage.trim(),
          customer_location: prefecture.trim(),
          prefecture: prefecture.trim(),
        },
        8,
      );
      setResults(list);
      setHasSearched(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '検索に失敗しました');
      setHasSearched(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mb-6 rounded-2xl border border-slate-200/90 bg-white shadow-sm">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left transition hover:bg-slate-50/80"
        aria-expanded={open}
      >
        <div>
          <h2 className="text-base font-semibold text-slate-900">工場マッチング（補助）</h2>
          <p className="mt-0.5 text-sm text-slate-500">
            症状から提携工場候補を探すときに使います。通常の案件対応は下の「案件一覧」から行ってください。
          </p>
        </div>
        <span className="shrink-0 text-slate-400">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="border-t border-slate-100 px-5 pb-5 pt-2">
          <div className="grid gap-4 md:grid-cols-1">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">カテゴリ</label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="例：エアコン、バッテリー、水回り"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">症状・メッセージ</label>
              <textarea
                value={userMessage}
                onChange={(e) => setUserMessage(e.target.value)}
                placeholder="例：エアコンが効かない、冷房が効かない"
                rows={3}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">所在地（都道府県）</label>
              <input
                type="text"
                value={prefecture}
                onChange={(e) => setPrefecture(e.target.value)}
                placeholder="例：東京都、大阪府"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleSearch}
              disabled={loading}
              className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading ? '検索中…' : '工場を検索'}
            </button>
            <button
              type="button"
              disabled
              title="案件に紐づけた自動割り当ては、管理者画面または案件単位のフローで実行します。"
              className="inline-flex cursor-not-allowed items-center justify-center rounded-xl border border-slate-200 bg-slate-100 px-4 py-2.5 text-sm font-medium text-slate-500"
            >
              自動割り当て（要案件指定）
            </button>
          </div>

          {error && (
            <p className="mt-3 text-sm text-red-600" role="alert">
              {error}
            </p>
          )}

          {results.length > 0 && (
            <ul className="mt-4 space-y-2">
              {results.map((f, i) => (
                <li
                  key={`${f.factory_id ?? f.name ?? 'f'}-${i}`}
                  className="rounded-lg border border-slate-200 bg-slate-50/80 px-3 py-2 text-sm"
                >
                  <div className="font-medium text-slate-900">{f.name ?? '（名称なし）'}</div>
                  <div className="mt-1 text-slate-600">
                    {f.prefecture && <span>{f.prefecture} · </span>}
                    スコア: {typeof f.matching_score === 'number' ? f.matching_score.toFixed(2) : '—'}
                  </div>
                  {f.specialties && f.specialties.length > 0 && (
                    <div className="mt-1 text-xs text-slate-500">
                      {f.specialties.join('、')}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}

          {!loading && hasSearched && !error && results.length === 0 && (
            <p className="mt-3 text-sm text-slate-600">該当する工場候補が見つかりませんでした。</p>
          )}
          {!loading && !hasSearched && !error && open && (
            <p className="mt-3 text-sm text-slate-500">条件を入れて「工場を検索」を押すと候補が表示されます。</p>
          )}
        </div>
      )}
    </section>
  );
}
