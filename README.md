# 🚐 キャンピングカー修理チャットボット

Notion統合型の最強キャンピングカー修理サポートシステム

## 🌟 主な機能

### 1. 💬 AI チャットボット
- OpenAI GPT-4搭載
- 自然な会話で修理相談
- 過去の会話履歴を記憶

### 2. 🔍 修理アドバイスセンター
- **Notion統合検索**
- 費用目安の自動表示
- 難易度・推定時間の表示
- 柔軟なキーワード検索

### 3. 🩺 診断フロー
- Notionベースの診断システム
- インタラクティブな質問フロー
- 症状に基づいた原因特定

### 4. 📚 ナレッジベース (RAG)
- ChromaDBによるベクトル検索
- 24カテゴリの修理情報
- リアルタイム検索

## 🏗️ システム構成

### バックエンド
- **Flask** - Webフレームワーク
- **Python 3.10+** - プログラミング言語
- **Gunicorn** - WSGIサーバー

### データソース
- **Notion Database** - メインデータストア
  - 修理ケースDB
  - 診断フローDB
  - 部品・工具DB
  - ナレッジベースDB
- **ChromaDB** - ベクトル検索
- **OpenAI Embeddings** - テキスト埋め込み

### AI・検索
- **OpenAI GPT-4** - AI応答生成
- **LangChain** - AI統合フレームワーク
- **SERP API** - リアルタイム価格検索（オプション）

## 📦 主要な依存関係

```
Flask>=2.3.0
Flask-CORS>=4.0.0
langchain>=0.1.0
langchain-openai>=0.1.0
python-dotenv>=1.0.0
notion-client>=2.2.1
aiohttp>=3.8.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
openai>=1.0.0
requests>=2.31.0
gunicorn>=21.2.0
```

## 🚀 ローカルセットアップ

### 1. リポジトリをクローン

```bash
git clone [your-repo-url]
cd camper-repair-clean
```

### 2. 環境変数を設定

`env.example`を参考に環境変数を設定：

```bash
# .envファイルを作成
OPENAI_API_KEY=your_openai_api_key
NOTION_API_KEY=your_notion_api_key
NODE_DB_ID=your_diagnostic_flow_db_id
CASE_DB_ID=your_repair_case_db_id
ITEM_DB_ID=your_parts_tools_db_id
KNOWLEDGE_BASE_DB_ID=2d099e34964341d4ba39b291f24d6b6b
```

### 3. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 4. バックエンドを起動

```bash
python unified_backend_api.py
```

### 5. ブラウザでアクセス

```
http://localhost:5002
```

## 🌐 Railwayデプロイ

詳細は `RAILWAY_DEPLOY_GUIDE.md` を参照してください。

### クイックデプロイ

1. GitHubにプッシュ
2. [Railway](https://railway.app)でプロジェクト作成
3. 環境変数を設定
4. デプロイ完了！

## 📁 プロジェクト構造

```
camper-repair-clean/
├── unified_backend_api.py      # メインFlaskアプリ
├── enhanced_rag_system.py      # RAGシステム
├── data_access/
│   └── notion_client.py        # Notion統合
├── templates/
│   ├── unified_chatbot.html    # メインUI
│   └── repair_advice_center.html # 検索UI
├── category_definitions.json   # カテゴリ定義
├── requirements_railway.txt    # 本番依存関係
├── Procfile                    # Railway設定
├── railway.json                # Railway設定
└── RAILWAY_DEPLOY_GUIDE.md     # デプロイガイド
```

## 🔧 主要機能の実装

### 1. 柔軟な検索機能

キーワード抽出により自然な文章での検索が可能：

```python
# 「雨漏りがする」→ 「雨漏り」を抽出
# 助詞・動詞を自動除去
# 複数キーワードでOR検索
```

### 2. Notion統合

修理ケースDB優先の検索ロジック：

```python
1. 修理ケースDBを検索（費用情報あり）
2. 結果がなければ診断フローDBを検索
3. それでもなければ一般アドバイスを提供
```

### 3. 費用情報の表示

Notionから以下を自動取得：

- 💰 費用目安（詳細な内訳）
- ⚙️ 難易度（初級/中級/上級）
- ⏱️ 推定時間

## 🎯 使用例

### 修理検索

```
ユーザー: 「雨漏りがする」

システム: 
🔧 CASE-009
💰 費用目安:
  • 診断料：3,000〜5,000円
  • シーリング材交換：5,000〜15,000円
  • 窓枠修理：10,000〜30,000円
⚙️ 難易度: 中級
⏱️ 推定時間: 1時間〜4時間
```

### AI チャット

```
ユーザー: 「バッテリーが上がりやすいのですが、原因は何でしょうか？」

AI: 「バッテリーが上がりやすい場合、以下の原因が考えられます：
1. バッテリーの劣化（寿命3-5年）
2. オルタネーターの故障
3. 電装品の電力消費
...」
```

## 🔒 セキュリティ

- 環境変数に機密情報を保存
- `.gitignore`でAPIキーを除外
- Notion APIキーの権限を最小限に設定
- CORS設定を適切に管理

## 📊 カテゴリ一覧

24カテゴリの修理情報を網羅：

- 🔋 バッテリー
- ❄️ エアコン
- 🚽 トイレ
- 💧 水道ポンプ
- 🌧️ 雨漏り
- 🔌 インバーター
- ☀️ ソーラーパネル
- 🚪 ドア・窓
- 🔥 FFヒーター
- その他15カテゴリ

## 🛠️ 開発

### テストの実行

```bash
# 検索システムのテスト
python test_fixed_search.py

# 柔軟な検索のテスト
python test_flexible_search.py

# Notion接続のテスト
python debug_knowledge_base.py
```

### デバッグモード

```bash
# Flask開発サーバー
export FLASK_DEBUG=True
python unified_backend_api.py
```

## 📝 ライセンス

このプロジェクトは私的使用を目的としています。

## 🤝 貢献

プルリクエストを歓迎します！

## 📞 サポート

問題が発生した場合は、Issueを作成してください。

## 🎉 今後の予定

- [ ] ユーザー認証機能
- [ ] 修理履歴の保存
- [ ] モバイルアプリ対応
- [ ] 画像アップロード機能
- [ ] 多言語対応

---

**Powered by:**
- 🤖 OpenAI GPT-4
- 📝 Notion API
- 🔍 ChromaDB
- 🚂 Railway
- ⚡ Flask

Made with ❤️ for キャンピングカー enthusiasts
