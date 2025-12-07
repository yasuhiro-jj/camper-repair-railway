import Hero from './components/Hero';
import Problem from './components/Problem';
import Features from './components/Features';
import Flow from './components/Flow';
import CTA from './components/CTA';
import Footer from './components/Footer';

export default function LPCamperRepairPage() {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

  // 構造化データ（LocalBusiness）
  const localBusinessData = {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: 'キャンピングカー修理工場マッチング（お客様用）',
    description: 'キャンピングカーの修理ができる業者・工場を簡単に探せるマッチングサービス。お客様向けのマッチングサービスです。',
    url: `${baseUrl}/lp-camper-repair`,
    areaServed: {
      '@type': 'Country',
      name: 'JP',
    },
  };

  return (
    <>
      {/* 構造化データ: LocalBusiness */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(localBusinessData) }}
      />
      <main className="min-h-screen">
        <Hero />
        <Problem />
        <Features />
        <Flow />
        <CTA />
        <Footer />
      </main>
    </>
  );
}
