# 🚀 Vercel フロントエンドデプロイガイド

## 📋 概要

このガイドでは、Next.jsフロントエンドアプリケーションをVercelにデプロイする手順を説明します。

**前提条件**:
- バックエンドは既にRailwayにデプロイ済み（昨日デプロイ）
- GitHubリポジトリにコードがプッシュ済み
- Vercelアカウント（GitHubアカウントでサインアップ可能）

---

## 🎯 デプロイ手順

### 1. Vercelアカウントの作成

1. https://vercel.com にアクセス
2. 「Sign Up」をクリック
3. GitHubアカウントでサインアップ（推奨）

### 2. プロジェクトのインポート

1. Vercelダッシュボードで「Add New...」→「Project」をクリック
2. GitHubリポジトリを選択
   - リポジトリが見つからない場合は、「Import Git Repository」で検索
3. プロジェクト設定を確認：
   - **Framework Preset**: `Next.js`（自動検出されるはず）
   - **Root Directory**: `frontend` を指定 ⚠️ **重要**
   - **Build Command**: `npm run build`（自動設定）
   - **Output Directory**: `.next`（自動設定）
   - **Install Command**: `npm install`（自動設定）

### 3. 環境変数の設定

**重要**: バックエンドAPIのURLを設定する必要があります。

#### 環境変数の追加

Vercelのプロジェクト設定画面で「Environment Variables」セクションに移動し、以下を追加：

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.railway.app` | バックエンドAPIのURL（RailwayのデプロイURL） |

**設定方法**:
1. 「Environment Variables」セクションを開く
2. 「Add New」をクリック
3. Key: `NEXT_PUBLIC_API_URL`
4. Value: バックエンドのRailway URL（例: `https://your-backend.railway.app`）
5. Environment: `Production`, `Preview`, `Development` すべてにチェック
6. 「Save」をクリック

**バックエンドURLの確認方法**:
- Railwayダッシュボードにログイン
- デプロイ済みのプロジェクトを選択
- 「Settings」→「Domains」でURLを確認
- または「Deployments」→最新のデプロイメントのURLを確認

### 4. デプロイの実行

1. 設定を確認後、「Deploy」をクリック
2. ビルドプロセスが開始されます（通常1-3分）
3. デプロイが完了すると、以下のようなURLが生成されます：
   - `https://your-project.vercel.app`

### 5. 動作確認

デプロイ完了後、以下のURLにアクセスして動作確認：

- **ホームページ**: `https://your-project.vercel.app`
- **チャットページ**: `https://your-project.vercel.app/chat`
- **工場ダッシュボード**: `https://your-project.vercel.app/factory`
- **管理者画面**: `https://your-project.vercel.app/admin`
- **LP（お客様用）**: `https://your-project.vercel.app/lp-camper-repair`
- **LP（パートナー募集）**: `https://your-project.vercel.app/lp-partner-recruit`

---

## 🔧 トラブルシューティング

### ビルドエラーが発生する場合

1. **Root Directoryが正しく設定されているか確認**
   - Root Directory: `frontend` が設定されている必要があります

2. **Node.jsバージョンの確認**
   - Vercelの設定で「Node.js Version」を確認
   - 推奨: `18.x` または `20.x`

3. **依存関係のエラー**
   ```bash
   # ローカルで確認
   cd frontend
   npm install
   npm run build
   ```

### バックエンドAPIに接続できない場合

1. **環境変数が正しく設定されているか確認**
   - Vercelの「Environment Variables」で `NEXT_PUBLIC_API_URL` が設定されているか
   - 値が正しいか（`https://`で始まるか、末尾に`/`がないか）

2. **バックエンドが起動しているか確認**
   - Railwayダッシュボードでバックエンドのステータスを確認
   - ログでエラーがないか確認

3. **CORS設定の確認**
   - バックエンドのCORS設定でVercelのドメインが許可されているか確認
   - `unified_backend_api.py`のCORS設定を確認

### 環境変数が反映されない場合

1. **再デプロイを実行**
   - 環境変数を変更した後は、再デプロイが必要です
   - 「Deployments」タブから「Redeploy」をクリック

2. **ビルドログを確認**
   - デプロイログで環境変数が正しく読み込まれているか確認

---

## 📝 カスタムドメインの設定（オプション）

1. Vercelのプロジェクト設定で「Domains」を開く
2. カスタムドメインを追加
3. DNS設定を更新（Vercelの指示に従う）

---

## 🔄 自動デプロイの設定

デフォルトで、GitHubリポジトリにプッシュすると自動的にデプロイされます。

### ブランチごとのデプロイ

- **`main`ブランチ**: Production環境にデプロイ
- **その他のブランチ**: Preview環境にデプロイ（プレビューURLが生成される）

### デプロイの無効化

特定のブランチの自動デプロイを無効にする場合：
1. 「Settings」→「Git」
2. 「Ignored Build Step」で条件を設定

---

## ✅ デプロイチェックリスト

- [ ] Vercelアカウントを作成
- [ ] GitHubリポジトリをインポート
- [ ] Root Directory: `frontend` を設定
- [ ] Framework Preset: `Next.js` を確認
- [ ] 環境変数 `NEXT_PUBLIC_API_URL` を設定（バックエンドのRailway URL）
- [ ] デプロイを実行
- [ ] ホームページが表示されることを確認
- [ ] チャットページでバックエンドAPIに接続できることを確認
- [ ] エラーがないかブラウザのコンソールを確認

---

## 📚 関連ドキュメント

- [Vercel公式ドキュメント](https://vercel.com/docs)
- [Next.js公式ドキュメント](https://nextjs.org/docs)
- [Railwayデプロイガイド](../RAILWAY_DEPLOY_GUIDE.md)
- [フロントエンド起動ガイド](../FRONTEND_STARTUP_GUIDE.md)

---

## 🆘 サポート

問題が発生した場合：
1. Vercelのデプロイログを確認
2. ブラウザのコンソールでエラーを確認
3. Railwayのバックエンドログを確認
4. 環境変数の設定を再確認

