# キャンピングカー修理チャットボット - Frontend

Next.js + TypeScript + Tailwind CSSで構築されたフロントエンドアプリケーション

## 🚀 セットアップ

### 1. フロントエンドディレクトリに移動

```bash
# プロジェクトルートから
cd frontend

# または、直接パスを指定
cd C:\Users\user\Desktop\udemy-langchain\camper-repair-clean\frontend
```

### 2. 依存関係のインストール

```bash
npm install
```

**注意**: 初回のみ実行してください。既にインストール済みの場合はスキップできます。

### 3. 環境変数の設定

`.env.local`ファイルを作成して、以下を設定してください：

**ファイルパス**: `frontend/.env.local`

**内容**:
```env
NEXT_PUBLIC_API_URL=https://web-production-c8b78.up.railway.app
```

**Windowsで作成する場合**:
```bash
# コマンドプロンプト
echo NEXT_PUBLIC_API_URL=https://web-production-c8b78.up.railway.app > .env.local

# PowerShell
Set-Content -Path .env.local -Value "NEXT_PUBLIC_API_URL=https://web-production-c8b78.up.railway.app"
```

**Vercel環境変数の設定**:
Vercelにデプロイしている場合、Vercelダッシュボードで環境変数を設定してください：
1. Vercelダッシュボード → プロジェクト選択 → Settings → Environment Variables
2. `NEXT_PUBLIC_API_URL` = `https://web-production-c8b78.up.railway.app` を追加
3. Production, Preview, Development すべてにチェック
4. 保存後、再デプロイ

### 4. 開発サーバーの起動

```bash
npm run dev
```

### 5. ブラウザで確認

開発サーバーが起動すると、以下のメッセージが表示されます：

```
  ▲ Next.js 16.0.3
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in X.XXs
```

ブラウザで以下のURLにアクセスしてください：

- **ホームページ**: http://localhost:3000 または http://localhost:3001
- **チャットページ**: http://localhost:3000/chat
- **工場ダッシュボード**: http://localhost:3000/factory
- **管理者画面**: http://localhost:3000/admin

**注意**: ポート3000が使用中の場合は、自動的に3001に切り替わります。

---

## 📖 詳細な起動手順

より詳しい起動手順やトラブルシューティングについては、[FRONTEND_STARTUP_GUIDE.md](../FRONTEND_STARTUP_GUIDE.md)を参照してください。

## 📁 プロジェクト構造

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # ルートレイアウト
│   ├── page.tsx           # ホームページ
│   ├── chat/              # チャットUI
│   ├── factory/           # 工場ダッシュボード
│   └── admin/             # 管理者画面
├── components/            # Reactコンポーネント
├── lib/                   # ユーティリティ関数
│   └── api.ts            # APIクライアント
├── types/                 # TypeScript型定義
└── public/                # 静的ファイル
```

## 🔧 技術スタック

- **Next.js 16** - Reactフレームワーク
- **TypeScript** - 型安全性
- **Tailwind CSS** - スタイリング
- **Axios** - HTTPクライアント

## 📝 開発の流れ

1. **チャットUIの実装** (`app/chat/page.tsx`)
2. **工場ダッシュボードの実装** (`app/factory/page.tsx`)
3. **管理者画面の実装** (`app/admin/page.tsx`)
4. **SEO強化** (メタタグ、構造化データ)

## 🔗 バックエンドAPI

既存のFlaskバックエンド (`unified_backend_api.py`) と通信します。

主要なエンドポイント:
- `POST /api/unified/chat` - チャットメッセージ送信
- `GET /api/factory/cases` - 工場案件一覧取得
- `GET /api/admin/factory-network` - 工場ネットワーク情報取得
