import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "協力会社募集 | キャンピングカー修理プラットフォーム",
  description: "キャンピングカー修理の協力会社を募集しています。AIを活用した修理プラットフォームで、新しい顧客獲得のチャンスを。登録費用無料、成功報酬型の手数料システム。",
  keywords: [
    "キャンピングカー修理",
    "協力会社募集",
    "修理店登録",
    "パートナー募集",
    "RV修理",
  ],
  openGraph: {
    title: "協力会社募集 | キャンピングカー修理プラットフォーム",
    description: "キャンピングカー修理の協力会社を募集しています。AIを活用した修理プラットフォームで、新しい顧客獲得のチャンスを。",
    type: "website",
  },
};

export default function RecruitPartnerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
