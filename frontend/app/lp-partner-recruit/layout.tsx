import type { Metadata } from "next";

const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

export const metadata: Metadata = {
  metadataBase: new URL(baseUrl),
  title: "キャンピングカー修理パートナー募集 | 専門業者でなくてもOK",
  description: "キャンピングカー修理ができる業者さん募集！大工・公務店・自動車整備工場・個人職人の方も歓迎。全国からの修理依頼をあなたの会社に送客します。登録無料。",
  keywords: [
    "キャンピングカー修理",
    "パートナー募集",
    "修理工場",
    "大工",
    "公務店",
    "自動車整備工場",
    "個人職人",
    "副業",
  ],
  authors: [{ name: "キャンピングカー修理サポートセンター" }],
  openGraph: {
    type: "website",
    locale: "ja_JP",
    url: `${baseUrl}/lp-partner-recruit`,
    siteName: "キャンピングカー修理パートナー募集",
    title: "キャンピングカー修理パートナー募集 | 専門業者でなくてもOK",
    description: "キャンピングカー修理ができる業者さん募集！大工・公務店・自動車整備工場・個人職人の方も歓迎。全国からの修理依頼をあなたの会社に送客します。",
    images: [
      {
        url: `${baseUrl}/og-image.png`,
        width: 1200,
        height: 630,
        alt: "キャンピングカー修理パートナー募集",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "キャンピングカー修理パートナー募集 | 専門業者でなくてもOK",
    description: "キャンピングカー修理ができる業者さん募集！大工・公務店・自動車整備工場・個人職人の方も歓迎。",
    images: [`${baseUrl}/og-image.png`],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function PartnerRecruitLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

