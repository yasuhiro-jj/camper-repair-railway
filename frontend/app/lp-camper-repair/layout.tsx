import type { Metadata } from "next";

const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

export const metadata: Metadata = {
  metadataBase: new URL(baseUrl),
  title: "全国どこでも修理可能 | キャンピングカー修理工場マッチング（お客様用）",
  description: "キャンピングカーの修理ができる業者・工場を簡単に探せます。修理工場・大工・公務店・自動車整備工場まで幅広く対応。AI診断で最適な修理業者を自動マッチング。お客様向けのマッチングサービスです。",
  keywords: [
    "キャンピングカー修理",
    "修理工場",
    "大工",
    "公務店",
    "自動車整備工場",
    "RV修理",
    "マッチング",
    "AI診断",
  ],
  authors: [{ name: "キャンピングカー修理サポートセンター" }],
  openGraph: {
    type: "website",
    locale: "ja_JP",
    url: `${baseUrl}/lp-camper-repair`,
    siteName: "キャンピングカー修理工場マッチング（お客様用）",
    title: "全国どこでも修理可能 | キャンピングカー修理工場マッチング（お客様用）",
    description: "キャンピングカーの修理ができる業者・工場を簡単に探せます。AI診断で最適な修理業者を自動マッチング。お客様向けのマッチングサービスです。",
    images: [
      {
        url: `${baseUrl}/og-image.png`,
        width: 1200,
        height: 630,
        alt: "キャンピングカー修理工場マッチング",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "全国どこでも修理可能 | キャンピングカー修理工場マッチング（お客様用）",
    description: "キャンピングカーの修理ができる業者・工場を簡単に探せます。AI診断で最適な修理業者を自動マッチング。お客様向けのマッチングサービスです。",
    images: [`${baseUrl}/og-image.png`],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function LPLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

