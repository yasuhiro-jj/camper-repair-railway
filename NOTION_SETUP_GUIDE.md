# 📊 Notionデータベース活用ガイド

## ✅ 現在の実装状況

プロジェクトには**完全なNotionデータベース連携機能**が実装されています！

### 🔧 実装済み機能

1. **NotionClient クラス** - 非同期対応・キャッシュ対応
2. **診断フローDB連携** - 診断ノードの管理
3. **修理ケースDB連携** - 修理事例の検索
4. **アイテムDB連携** - 部品・工具情報
5. **自動キャッシュ機能** - 高速レスポンス
6. **エラーハンドリング** - 堅牢な接続管理

## 🚀 セットアップ手順

### 1. 必要なパッケージのインストール

```bash
pip install notion-client python-dotenv aiohttp
```

### 2. Notion APIキーの取得

1. **Notion開発者ページにアクセス**
   - https://www.notion.so/my-integrations

2. **新しいインテグレーションを作成**
   - "New integration" をクリック
   - 名前: "キャンピングカー修理ボット"
   - ワークスペース: あなたのNotionワークスペースを選択

3. **APIキーをコピー**
   - Internal Integration Token をコピー
   - 形式: `secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 3. データベースの準備

#### 必要なデータベース（3つ）

1. **診断フローDB** - 診断ノード管理
2. **修理ケースDB** - 修理事例管理  
3. **アイテムDB** - 部品・工具管理

#### データベースIDの取得方法

1. Notionでデータベースページを開く
2. URLからIDを抽出
   ```
   https://www.notion.so/your-workspace/DATABASE_ID?v=...
   ```
3. ハイフンを削除 [[memory:8850961]]

### 4. 環境変数の設定

`.env` ファイルに以下を追加：

```env
# Notion API設定
NOTION_API_KEY=secret_your_actual_api_key_here

# データベースID（ハイフンなし）
NODE_DB_ID=your_diagnostic_flow_database_id
CASE_DB_ID=your_repair_case_database_id  
ITEM_DB_ID=your_item_database_id

# 代替設定（旧バージョン対応）
NOTION_DIAGNOSTIC_DB_ID=your_diagnostic_flow_database_id
NOTION_REPAIR_CASE_DB_ID=your_repair_case_database_id
```

### 5. データベース権限の設定

各データベースページで：
1. 右上の "Share" をクリック
2. 作成したインテグレーションを招待
3. "Can edit" 権限を付与

### 6. 接続テスト

```bash
python test_notion_connection.py
```

## 📋 データベース構造例

### 診断フローDB（NODE_DB_ID）

| プロパティ名 | タイプ | 説明 |
|-------------|--------|------|
| Title | Title | ノード名 |
| Category | Select | カテゴリ（バッテリー、エアコン等） |
| Question | Rich Text | 診断質問 |
| Options | Multi-select | 選択肢 |
| Next Nodes | Relation | 次のノード |

### 修理ケースDB（CASE_DB_ID）

| プロパティ名 | タイプ | 説明 |
|-------------|--------|------|
| Title | Title | ケース名 |
| Category | Select | カテゴリ |
| Symptoms | Multi-select | 症状 |
| Solution | Rich Text | 解決方法 |
| Cost | Number | 費用目安 |
| Parts | Relation | 必要な部品 |

### アイテムDB（ITEM_DB_ID）

| プロパティ名 | タイプ | 説明 |
|-------------|--------|------|
| Name | Title | 部品名 |
| Type | Select | タイプ（部品、工具） |
| Price | Number | 価格 |
| Description | Rich Text | 説明 |
| URL | URL | 購入リンク |

## 🔧 使用方法

### 1. Streamlitアプリでの使用

```python
from data_access.notion_client import NotionClient

# クライアント初期化
notion = NotionClient()

# 診断データの読み込み
diagnostic_data = notion.load_diagnostic_data()

# 修理ケースの検索
repair_cases = notion.search_repair_cases("バッテリー上がり")
```

### 2. 非同期使用

```python
import asyncio

async def main():
    notion = NotionClient()
    
    # 非同期でデータ取得
    data = await notion.get_diagnostic_nodes_async()
    print(data)

asyncio.run(main())
```

## 🎯 活用例

### 1. 診断フローシステム
- ユーザーの症状から適切な診断フローを表示
- 段階的な質問で原因を特定
- 関連する修理ケースを自動表示

### 2. 修理アドバイス
- 症状に基づく修理方法の提案
- 費用目安の自動計算
- 必要な部品のリスト表示

### 3. 部品検索
- 修理に必要な部品の検索
- 価格比較情報
- 購入リンクの提供

## ⚠️ 注意事項

1. **APIキーの管理**
   - `.env`ファイルを`.gitignore`に追加
   - 本番環境では環境変数で管理

2. **データベースID**
   - ハイフンは含めない [[memory:8850961]]
   - 32文字の英数字文字列

3. **権限設定**
   - インテグレーションに適切な権限を付与
   - 必要最小限の権限に留める

4. **レート制限**
   - Notion APIにはレート制限あり
   - キャッシュ機能で軽減

## 🚨 トラブルシューティング

### よくある問題

1. **APIキーエラー**
   ```
   ❌ Notion APIキーが設定されていません
   ```
   → `.env`ファイルの`NOTION_API_KEY`を確認

2. **データベースIDエラー**
   ```
   ❌ 診断フローDBのIDが設定されていません
   ```
   → データベースIDを正しく設定し、ハイフンを削除

3. **権限エラー**
   ```
   HTTP 403: Forbidden
   ```
   → データベースにインテグレーションを招待

4. **接続エラー**
   ```
   HTTP 401: Unauthorized
   ```
   → APIキーが正しいか確認

### デバッグ方法

```bash
# 接続テスト
python test_notion_connection.py

# データベース構造確認
python check_notion_structure.py

# 詳細ログ有効化
export NOTION_DEBUG=true
```

## 🎉 完了！

Notionデータベースが正常に動作すれば、以下の機能が利用できます：

- ✅ 診断フローシステム
- ✅ 修理ケース検索
- ✅ 部品情報管理
- ✅ 費用見積もり
- ✅ 自動キャッシュ
- ✅ リアルタイム更新

**次のステップ**: Streamlitアプリを起動してNotion機能をテストしてください！