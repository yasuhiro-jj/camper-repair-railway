import Link from "next/link";

const DIAGNOSIS_URL = "https://web-production-c8b78.up.railway.app/";
const LINE_URL = "https://line.me/R/ti/p/@okayama-camper";

export default function Hero() {
  return (
    <section className="rounded-3xl bg-slate-900 px-8 py-12 text-white shadow-xl">
      <div className="space-y-6">
        <p className="inline-flex items-center rounded-full bg-white/10 px-4 py-1 text-sm font-medium tracking-wide text-yellow-300">
          キャンピングカー修理ガイド × 診断アプリ × LINE相談
        </p>
        <div className="space-y-4">
          <h1 className="text-4xl font-semibold leading-tight sm:text-5xl">
            キャンピングカー修理の不安を診断で見える化し、不安解消へ。
          </h1>
          <p className="text-lg text-slate-100">
            キャンピングカーのエアコン・FFヒーター・電装・車体まで、
            症状別に原因と対処を整理できる修理ガイドです。迷ったら3分診断とLINE相談に繋がります。
          </p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link
            href={DIAGNOSIS_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center rounded-full bg-yellow-400 px-6 py-3 text-base font-semibold text-slate-900 transition hover:bg-yellow-300"
          >
            3分で診断する
          </Link>
          <Link
            href={LINE_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center rounded-full border border-white/40 px-6 py-3 text-base font-semibold transition hover:bg-white/10"
          >
            LINEで相談する
          </Link>
        </div>
        <div className="grid gap-6 border-t border-white/10 pt-6 text-sm md:grid-cols-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-300">主な診断カテゴリ</p>
            <p className="font-semibold text-white">エアコン / FFヒーター / 電装</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-300">診断精度</p>
            <p className="font-semibold text-white">症状ヒアリング＋Notionナレッジで可視化</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-300">対応チャネル</p>
            <p className="font-semibold text-white">Railway診断 & LINE相談で即フォロー</p>
          </div>
        </div>
      </div>
    </section>
  );
}




