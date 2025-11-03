#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotionデータベースIDの取得方法ガイド
"""

print("=" * 60)
print("📋 NotionデータベースIDの取得方法")
print("=" * 60)

print("""
🔍 方法1: NotionのURLから取得

1. Notionで「🗒️ Chat Logs DB」を開く
2. ブラウザのアドレスバーを確認
3. URLの形式は以下のようになっています:

   https://www.notion.so/workspace/029bdc77fc23411390d3de6595b07dfe?v=...

4. この「029bdc77fc23411390d3de6595b07dfe」の部分がデータベースIDです
5. ハイフンは含めず、そのまま使用してください

⚠️ 注意: データベースIDは32文字の英数字です
""")

print("""
🔍 方法2: NotionのShareから取得

1. データベースページの右上「Share」をクリック
2. 「Copy link」をクリック
3. コピーされたURLからIDを抽出
4. URLの形式: https://www.notion.so/workspace/DATABASE_ID?v=...
""")

print("""
🔍 方法3: データベースがページ内にある場合

データベースがページ内に埋め込まれている場合:
1. データベースの右上「...」メニューを開く
2. 「Copy link」を選択
3. URLからIDを抽出
""")

print("=" * 60)
print("✅ アクセス権限の確認")
print("=" * 60)

print("""
インテグレーションにアクセス権限があるか確認:

1. データベースページの右上「Share」をクリック
2. 「Add people, emails, groups, or integrations」をクリック
3. インテグレーション名（例: "Camper Repair System"）を検索
4. インテグレーションが表示されない場合:
   → 「Add people」の代わりに「Add integrations」を選択
   → 利用可能なインテグレーション一覧から選択
5. 権限を「Can edit」または「Full access」に設定
""")

print("=" * 60)
print("🔧 次のステップ")
print("=" * 60)

print("""
1. 正しいデータベースIDを確認
2. .envファイルのNOTION_LOG_DB_IDを更新
3. インテグレーションのアクセス権限を確認
4. 再度 check_notion_chat_logs_db.py を実行
""")

print("=" * 60)
print("💡 データベースIDの例")
print("=" * 60)

print("""
正しい形式: 32文字の英数字（ハイフンなし）
例: 029bdc77fc23411390d3de6595b07dfe

間違った形式:
- 029bdc77-fc23-4113-90d3-de6595b07dfe（ハイフンを含む）
- 029bdc77fc23411390d3de6595b07df（31文字）
- 029bdc77fc23411390d3de6595b07dfee（33文字）
""")

