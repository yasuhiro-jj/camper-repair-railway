import type { Metadata } from 'next';

const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';

export const metadata: Metadata = {
  title: 'チャット - AI修理サポート',
  description: 'キャンピングカーの症状を入力するだけで、AIが原因を特定し、専門的な修理アドバイスを提供します。24時間対応、無料診断。',
  openGraph: {
    title: 'チャット - AI修理サポート | キャンピングカー修理チャットボット',
    description: 'キャンピングカーの症状を入力するだけで、AIが原因を特定し、専門的な修理アドバイスを提供します。',
    url: `${baseUrl}/chat`,
  },
};

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // FAQPage構造化データ
  const faqData = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'キャンピングカーの修理はどこでできますか？',
        acceptedAnswer: {
          '@type': 'Answer',
          text: '岡山キャンピングカー修理サポートセンターで対応しています。電話番号：086-206-6622、営業時間：平日 9:00〜18:00 | 土日祝 10:00〜17:00',
        },
      },
      {
        '@type': 'Question',
        name: 'AIチャットボットで何ができますか？',
        acceptedAnswer: {
          '@type': 'Answer',
          text: '症状を入力するだけで、AIが原因を特定し、専門的な修理アドバイスを提供します。24時間対応、無料診断・見積り対応。',
        },
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqData) }}
      />
      {children}
    </>
  );
}

