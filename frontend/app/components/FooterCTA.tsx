import Link from "next/link";

const DIAGNOSIS_URL = "https://web-production-c8b78.up.railway.app/";
const LINE_URL = "https://line.me/R/ti/p/@okayama-camper";

export default function FooterCTA() {
  return (
    <section className="rounded-3xl bg-slate-900 px-8 py-10 text-white">
      <div className="space-y-4 text-center">
        <p className="text-sm uppercase tracking-wide text-yellow-300">最後まで迷ったら</p>
        <h2 className="text-3xl font-semibold">診断とLINEの2本立てで不安をゼロに</h2>
        <p className="text-base text-slate-200">
          3分診断で症状を可視化し、その結果をLINE相談に引き継ぎ。全国の提携工場へシームレスに繋ぎます。
        </p>
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link
            href={DIAGNOSIS_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center rounded-full bg-yellow-400 px-6 py-3 text-base font-semibold text-slate-900 transition hover:bg-yellow-300"
          >
            無料診断を受ける
          </Link>
          <Link
            href={LINE_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center rounded-full border border-white/20 px-6 py-3 text-base font-semibold transition hover:bg-white/10"
          >
            LINEで相談する
          </Link>
        </div>
      </div>
    </section>
  );
}




