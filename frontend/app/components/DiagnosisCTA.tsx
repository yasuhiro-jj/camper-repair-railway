import Link from "next/link";

const DIAGNOSIS_URL = "https://web-production-c8b78.up.railway.app/";

export default function DiagnosisCTA() {
  return (
    <section className="rounded-3xl bg-gradient-to-br from-rose-600 via-red-600 to-red-500 px-8 py-10 text-white shadow-xl">
      <div className="space-y-4">
        <p className="text-sm font-semibold uppercase tracking-wide text-white/80">無料オンライン診断</p>
        <h2 className="text-3xl font-semibold leading-snug">
          困ったら、まずは3分で診断。<br />
          症状に答えるだけで、原因と次の一手がわかります。
        </h2>
        <p className="text-base text-white/90">
          ヒアリング内容はRailway上の診断アプリに連携し、Notionナレッジで裏付け。数値化されたチェックリストで見積もり前の不安を可視化します。
        </p>
        <Link
          href={DIAGNOSIS_URL}
          target="_blank"
          rel="noreferrer"
          className="inline-flex w-full items-center justify-center rounded-full bg-white px-6 py-3 text-lg font-semibold text-red-600 transition hover:bg-yellow-100 md:w-auto"
        >
          無料で3分診断を受ける
        </Link>
      </div>
    </section>
  );
}




