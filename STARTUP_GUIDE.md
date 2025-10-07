# 🚐 キャンピングカー修理AI 起動ガイド

## 📋 システム概要

このシステムは、キャンピングカーの修理に関するAI搭載のアドバイスシステムです。

### 🏗️ アーキテクチャ
- **フロントエンド**: Next.js + React + TypeScript
- **バックエンド**: Flask + Python
- **AI機能**: OpenAI GPT-4 + LangChain
- **検索機能**: Chroma Vector Store + SERP API

## 🚀 起動方法

### 方法1: 自動起動（推奨）

```bash
# フルスタックシステムを自動起動
cd frontend
start-full-stack.bat
```

### 方法2: 手動起動

#### 1. バックエンド起動
```bash
# プロジェクトルートで実行
python app.py
```

#### 2. フロントエンド起動
```bash
# フロントエンドディレクトリで実行
cd frontend
npm run dev
```

## 🌐 アクセスURL

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:5001
- **ヘルスチェック**: http://localhost:5001/api/health

## 🧪 統合テスト

```bash
# 統合テスト実行
python test_integration.py
```

## 📱 機能一覧

### 💬 チャット機能
- AIとの対話形式での修理相談
- リアルタイム回答生成
- 会話履歴の保持

### 🔍 検索機能
- 修理情報の詳細検索
- 修理手順の表示
- 費用目安の提供
- 注意事項の表示

### 📋 カテゴリ機能
- 修理カテゴリの一覧表示
- カテゴリ別の情報検索
- アイコン付きの直感的なUI

## 🔧 トラブルシューティング

### よくある問題

#### 1. バックエンドが起動しない
```bash
# 依存関係の確認
pip install -r requirements.txt

# 環境変数の確認
# .envファイルまたはconfig.pyの設定を確認
```

#### 2. フロントエンドが起動しない
```bash
# 依存関係のインストール
cd frontend
npm install

# ポートの確認
# 3000番ポートが使用中でないか確認
```

#### 3. API接続エラー
- バックエンドが起動しているか確認
- http://localhost:5001 にアクセスできるか確認
- ファイアウォールの設定を確認

### ログの確認

#### バックエンドログ
```bash
# バックエンドのログを確認
python app.py
# コンソールにエラーメッセージが表示されます
```

#### フロントエンドログ
```bash
# ブラウザの開発者ツール（F12）でコンソールを確認
# Network タブでAPIリクエストの状況を確認
```

## 📊 システム要件

### 最小要件
- Python 3.8+
- Node.js 16+
- 4GB RAM
- 2GB 空きディスク容量

### 推奨要件
- Python 3.9+
- Node.js 18+
- 8GB RAM
- 5GB 空きディスク容量

## 🔐 環境変数設定

### 必要なAPIキー
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# SERP API Key (オプション)
SERP_API_KEY=your_serp_api_key

# LangSmith API Key (オプション)
LANGSMITH_API_KEY=your_langsmith_api_key
```

### 設定ファイル
- `config.py`: メイン設定
- `.env`: 環境変数（オプション）
- `frontend/next.config.js`: フロントエンド設定

## 🎯 使用例

### チャット機能の使用例
1. フロントエンドにアクセス
2. 「💬 チャット相談」タブを選択
3. 「バッテリーが充電されない」と入力
4. AIの回答を確認

### 検索機能の使用例
1. 「🔍 情報検索」タブを選択
2. 「トイレ修理」と入力
3. 検索結果を確認
4. 修理手順や費用目安を確認

## 📞 サポート

### 問題報告
- GitHub Issues で問題を報告
- ログファイルを添付
- エラーメッセージの詳細を記載

### 機能要望
- 新機能の要望は GitHub Issues で提案
- 具体的な使用例を記載

## 🔄 更新履歴

### v1.0.0 (2024-01-15)
- 初期リリース
- チャット機能
- 検索機能
- カテゴリ機能
- エラーハンドリング

---

**🎉 システムの準備が完了しました！**

フロントエンドとバックエンドの両方が起動したら、http://localhost:3000 にアクセスしてシステムをお試しください。
