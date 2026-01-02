import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3001";

export const metadata: Metadata = {
  metadataBase: new URL(baseUrl),
  title: "キャンピングカー 修理｜診断・原因・対処ガイド",
  description:
    "キャンピングカーの修理不安を3分オンライン診断とLINE相談で可視化し、エアコンや電装など10カテゴリの記事とRAGナレッジで原因と対処を整理するハブメディアです。全国の提携工場へ繋がる診断導線も備え、費用感やリスク回避まで1ページで確認できます。",
  keywords: [
    "キャンピングカー",
    "修理",
    "メンテナンス",
    "チャットボット",
    "AI",
    "診断",
    "トラブルシューティング",
    "RV",
    "キャンピングカー修理",
    "岡山",
  ],
  authors: [{ name: "キャンピングカー修理サポートセンター" }],
  creator: "キャンピングカー修理サポートセンター",
  publisher: "キャンピングカー修理サポートセンター",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: "website",
    locale: "ja_JP",
    url: baseUrl,
    siteName: "キャンピングカー 修理｜診断・原因・対処ガイド",
    title: "キャンピングカー 修理｜診断・原因・対処ガイド",
    description:
      "カテゴリ別ガイドと3分診断・LINE相談で不安を解消するキャンピングカー修理メディア。Railway診断と提携工場マッチングに直結。",
    images: [
      {
        url: `${baseUrl}/og-image.png`,
        width: 1200,
        height: 630,
        alt: "キャンピングカー修理チャットボット",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "キャンピングカー 修理｜診断・原因・対処ガイド",
    description:
      "3分オンライン診断とLINE相談で不安を解消し、カテゴリ別記事で原因と対処がわかるハブ型メディア。",
    images: [`${baseUrl}/og-image.png`],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    // Google Search Console用の検証コードを追加可能
    // google: "your-google-verification-code",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';

  // 構造化データ（JSON-LD）
  const organizationData = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'キャンピングカー修理サポートセンター',
    url: baseUrl,
    logo: `${baseUrl}/logo.png`,
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: '+81-86-206-6622',
      contactType: 'customer service',
      areaServed: 'JP',
      availableLanguage: 'Japanese',
    },
    sameAs: ['https://camper-repair.net/blog/'],
  };

  const websiteData = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'キャンピングカー修理チャットボット',
    url: baseUrl,
    description: 'AI搭載のキャンピングカー修理サポートシステム',
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${baseUrl}/chat?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  };

  return (
    <html lang="ja">
      <head>
        {/* 構造化データ: Organization */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationData) }}
        />
        {/* 構造化データ: WebSite */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteData) }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
