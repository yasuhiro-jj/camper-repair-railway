export type Category = {
  name: string;
  description: string;
  slug: string;
};

/**
 * ルート (`/`) のカテゴリ一覧用データ。
 * `CategoryGrid` から参照されます。
 *
 * NOTE:
 * - `slug` は `/repair-advice?q=...` にして、クリック時に検索ページへ遷移できるようにしています。
 */
export const categories: Category[] = [
  {
    name: 'エアコン',
    description: '冷えない・異音・水漏れなどの切り分け',
    slug: '/repair-advice?q=エアコン',
  },
  {
    name: 'FFヒーター',
    description: '点火しない・途中停止・煙の原因',
    slug: '/repair-advice?q=FFヒーター',
  },
  {
    name: '電装',
    description: '配線・ヒューズ・充電系トラブル',
    slug: '/repair-advice?q=電装',
  },
  {
    name: 'バッテリー',
    description: 'サブバッテリー/走行充電/劣化診断',
    slug: '/repair-advice?q=バッテリー',
  },
  {
    name: 'インバーター',
    description: '警告・停止・容量不足の見直し',
    slug: '/repair-advice?q=インバーター',
  },
  {
    name: '水回り',
    description: '水道ポンプ・蛇口・タンクの不具合',
    slug: '/repair-advice?q=水道ポンプ',
  },
  {
    name: 'トイレ',
    description: 'カセット/マリンの詰まり・臭い対策',
    slug: '/repair-advice?q=トイレ',
  },
  {
    name: '雨漏り',
    description: 'ルーフ・窓・シーリングの劣化チェック',
    slug: '/repair-advice?q=雨漏り',
  },
  {
    name: '冷蔵庫',
    description: '冷えない・点火しない・切替不良',
    slug: '/repair-advice?q=冷蔵庫',
  },
  {
    name: 'ガス',
    description: 'ガス臭・着火不良・安全装置の確認',
    slug: '/repair-advice?q=ガス',
  },
];




