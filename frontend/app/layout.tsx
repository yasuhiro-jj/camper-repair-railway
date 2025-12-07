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

const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';

export const metadata: Metadata = {
  metadataBase: new URL(baseUrl),
  title: {
    default: "キャンピングカー修理チャットボット | AI搭載の修理サポート",
    template: "%s | キャンピングカー修理チャットボット",
  },
  description: "AI搭載のキャンピングカー修理サポートシステム。症状を入力するだけで、専門的な修理アドバイスを提供します。24時間対応、無料診断・見積り対応。",
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
    siteName: "キャンピングカー修理チャットボット",
    title: "キャンピングカー修理チャットボット | AI搭載の修理サポート",
    description: "AI搭載のキャンピングカー修理サポートシステム。症状を入力するだけで、専門的な修理アドバイスを提供します。",
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
    title: "キャンピングカー修理チャットボット | AI搭載の修理サポート",
    description: "AI搭載のキャンピングカー修理サポートシステム。症状を入力するだけで、専門的な修理アドバイスを提供します。",
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
