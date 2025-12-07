import Hero from './components/Hero';
import WhyUs from './components/WhyUs';
import Merits from './components/Merits';
import Flow from './components/Flow';
import Conditions from './components/Conditions';
import Pricing from './components/Pricing';
import Cases from './components/Cases';
import FAQ from './components/FAQ';
import PartnerForm from './components/PartnerForm';

export default function PartnerRecruitPage() {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

  // 構造化データ（LocalBusiness）
  const localBusinessData = {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: 'キャンピングカー修理パートナー募集',
    description: 'キャンピングカー修理ができる業者さん募集！大工・公務店・自動車整備工場・個人職人の方も歓迎。',
    url: `${baseUrl}/lp-partner-recruit`,
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
        <WhyUs />
        <Merits />
        <Flow />
        <Conditions />
        <Pricing />
        <Cases />
        <FAQ />
        <PartnerForm />
      </main>
    </>
  );
}

