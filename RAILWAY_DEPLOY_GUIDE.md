# 🚀 Railway デプロイガイド

## 📋 システム概要

**キャンピングカー修理チャットボット** - Notion統合型RAGシステム

- **バックエンド**: Flask + Python
- **データソース**: Notion Database（修理ケース、診断フロー、ナレッジベース）
- **AI**: OpenAI GPT-4
- **検索**: ChromaDB (RAG) + Notion API

## ✅ デプロイ前の確認事項

### 必須ファイル

- ✅ `unified_backend_api.py` - メインFlaskアプリ
- ✅ `requirements_railway.txt` - 依存関係
- ✅ `Procfile` - Railway起動コマンド
- ✅ `railway.json` - Railway設定
- ✅ `templates/unified_chatbot.html` - メインUI
- ✅ `templates/repair_advice_center.html` - 検索UI
- ✅ `data_access/notion_client.py` - Notion統合
- ✅ `enhanced_rag_system.py` - RAGシステム
- ✅ `category_definitions.json` - カテゴリ定義

### 必要なAPI

1. **OpenAI API**
   - https://platform.openai.com/api-keys
   - GPT-4アクセス権が必要

2. **Notion API**
   - https://www.notion.so/my-integrations
   - 統合（Integration）を作成
   - データベースへのアクセス権を付与

3. **Notionデータベース**
   - 診断フローDB
   - 修理ケースDB
   - 部品・工具DB
   - ナレッジベースDB

## 🔧 環境変数の準備

以下の環境変数を準備してください（`env.example`を参照）：

### 必須環境変数

```bash
# OpenAI API
OPENAI_API_KEY=sk-proj-...

# Notion API
NOTION_API_KEY=ntn_...

# NotionデータベースID（ハイフンなし）
NODE_DB_ID=254e9a7ee5b7807ea...
CASE_DB_ID=256e9a7ee5b78021...
ITEM_DB_ID=254e9a7ee5b780af...
KNOWLEDGE_BASE_DB_ID=2d099e34964341d4ba39b291f24d6b6b

# Flask設定
FLASK_ENV=production
FLASK_DEBUG=False
```

### オプション環境変数

```bash
# SERP API（価格検索用）
SERP_API_KEY=your_serp_api_key

# LangSmith（トレーシング用）
LANGSMITH_API_KEY=your_langsmith_api_key

# テキストファイル使用
USE_TEXT_FILES=false
```

## 🚀 Railwayデプロイ手順

### ステップ1: GitHubリポジトリの準備

```bash
# 現在のディレクトリで実行
git add .
git commit -m "Railway deployment ready"
git push origin main
```

### ステップ2: Railwayアカウント作成

1. [Railway.app](https://railway.app) にアクセス
2. GitHubアカウントでログイン
3. 「Start a New Project」をクリック

### ステップ3: プロジェクト作成

1. 「Deploy from GitHub repo」を選択
2. リポジトリを選択（例: `camper-repair-clean`）
3. 「Deploy Now」をクリック

### ステップ4: 環境変数設定

プロジェクトダッシュボードで「Variables」タブをクリックし、以下を追加：

| 変数名 | 値 | 必須 |
|--------|-----|------|
| `OPENAI_API_KEY` | あなたのOpenAI APIキー | ✅ |
| `NOTION_API_KEY` | あなたのNotion APIキー | ✅ |
| `NODE_DB_ID` | 診断フローDB ID（ハイフンなし） | ✅ |
| `CASE_DB_ID` | 修理ケースDB ID（ハイフンなし） | ✅ |
| `ITEM_DB_ID` | 部品・工具DB ID（ハイフンなし） | ✅ |
| `KNOWLEDGE_BASE_DB_ID` | `2d099e34964341d4ba39b291f24d6b6b` | ✅ |
| `FLASK_ENV` | `production` | ✅ |
| `FLASK_DEBUG` | `False` | ✅ |
| `SERP_API_KEY` | あなたのSERP APIキー | ❌ |
| `LANGSMITH_API_KEY` | あなたのLangSmith APIキー | ❌ |
| `USE_TEXT_FILES` | `false` | ❌ |

### ステップ5: デプロイ確認

1. 「Deployments」タブで最新のデプロイを確認
2. ログにエラーがないか確認
3. 「Settings」→「Domains」でカスタムドメインを設定（オプション）

### ステップ6: 動作テスト

デプロイされたURLにアクセスして以下を確認：

- ✅ トップページ（チャットボット）が表示される
- ✅ 修理アドバイスセンターで検索が動作する
- ✅ Notionデータベースから費用情報が表示される
- ✅ 診断フローが動作する

## 🔍 トラブルシューティング

### デプロイが失敗する場合

**1. ビルドエラー**
```bash
# Railwayのログを確認
# 「Deployments」→ 最新のデプロイ → 「View Logs」
```

**よくあるエラー:**
- `ModuleNotFoundError`: `requirements_railway.txt`に依存関係を追加
- `Port binding error`: `Procfile`の設定を確認

**2. 起動エラー**
```bash
# 環境変数が正しく設定されているか確認
# 「Variables」タブで全ての必須変数があるか確認
```

**3. Notion接続エラー**
- Notion APIキーが正しいか確認
- データベースIDがハイフンなしか確認
- Notion統合がデータベースにアクセス権があるか確認

### Notionデータベース IDの取得方法

Notionデータベース URLの例:
```
https://www.notion.so/254e9a7e-e5b7-807e-a...
```

ハイフンを除去:
```
254e9a7ee5b7807ea...
```

## 📝 デプロイ後のメンテナンス

### コードの更新

```bash
# ローカルで変更をコミット
git add .
git commit -m "Update: [変更内容]"
git push origin main

# Railwayが自動的に再デプロイ
```

### 環境変数の更新

1. Railwayダッシュボード → 「Variables」
2. 変数を編集
3. 「Save」をクリック（自動的に再起動）

### ログの確認

1. 「Deployments」→ 最新のデプロイ
2. 「View Logs」をクリック
3. エラーや警告を確認

## 🎯 本番環境のベストプラクティス

### セキュリティ

- ✅ 環境変数に機密情報を保存（コードに直接書かない）
- ✅ Notion APIキーの権限を最小限に
- ✅ CORS設定を適切に設定
- ✅ HTTPS通信を使用

### パフォーマンス

- ✅ ChromaDBのキャッシュを有効化
- ✅ Notion APIのレート制限に注意
- ✅ OpenAI APIのコストを監視

### モニタリング

- ✅ Railwayのメトリクスを定期的に確認
- ✅ エラーログを監視
- ✅ APIの使用量を追跡

## 📊 コスト見積もり

### Railway

- **Hobby Plan**: $5/月（500時間の実行時間）
- **Pro Plan**: 使用量に応じて課金

### OpenAI

- GPT-4: 使用量に応じて課金
- 平均的な使用量: $10-50/月

### Notion

- 無料プラン: APIアクセス可能
- Plus以上: チーム利用可能

## 🆘 サポート

### Railway

- ドキュメント: https://docs.railway.app
- Discord: https://discord.gg/railway

### その他

- Notion API: https://developers.notion.com
- OpenAI API: https://platform.openai.com/docs

## ✅ デプロイチェックリスト

デプロイ前に以下を確認してください：

- [ ] GitHubリポジトリが最新
- [ ] `.gitignore`が適切に設定されている
- [ ] `requirements_railway.txt`に全ての依存関係がある
- [ ] `Procfile`が正しい
- [ ] `railway.json`が設定されている
- [ ] 全ての必須環境変数を準備した
- [ ] Notion統合がデータベースにアクセス可能
- [ ] OpenAI APIキーが有効
- [ ] ローカルで動作確認済み

## 🎉 デプロイ完了後

デプロイが成功したら：

1. **URLを共有**
   - Railwayが提供するURL
   - カスタムドメイン（設定した場合）

2. **動作確認**
   - 全ての機能が正常に動作するか
   - 検索結果に費用情報が表示されるか
   - 診断フローが動作するか

3. **継続的改善**
   - ユーザーフィードバックを収集
   - パフォーマンスを監視
   - 新機能を追加

おめでとうございます！🎉 キャンピングカー修理チャットボットがRailwayにデプロイされました！
