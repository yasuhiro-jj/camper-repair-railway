#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notionデータベース接続テストスクリプト
"""

import os
import sys
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

def test_notion_connection():
    """Notion接続をテスト"""
    print("🔍 Notionデータベース接続テストを開始...")
    
    # APIキーの確認
    notion_api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    if not notion_api_key:
        print("❌ Notion APIキーが設定されていません")
        print("💡 .envファイルにNOTION_API_KEYを設定してください")
        return False
    
    print(f"✅ APIキー確認: {notion_api_key[:20]}...")
    
    # データベースIDの確認
    node_db_id = os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID")
    case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
    item_db_id = os.getenv("ITEM_DB_ID")
    
    print(f"📊 診断フローDB ID: {node_db_id or '未設定'}")
    print(f"📊 修理ケースDB ID: {case_db_id or '未設定'}")
    print(f"📊 アイテムDB ID: {item_db_id or '未設定'}")
    
    # Notionクライアントのテスト
    try:
        from notion_client import Client
        client = Client(auth=notion_api_key)
        print("✅ Notionクライアントの初期化に成功")
        
        # データベース接続テスト
        if node_db_id:
            try:
                database = client.databases.retrieve(database_id=node_db_id)
                print(f"✅ 診断フローDB接続成功: {database['title'][0]['text']['content']}")
            except Exception as e:
                print(f"❌ 診断フローDB接続失敗: {e}")
        
        if case_db_id:
            try:
                database = client.databases.retrieve(database_id=case_db_id)
                print(f"✅ 修理ケースDB接続成功: {database['title'][0]['text']['content']}")
            except Exception as e:
                print(f"❌ 修理ケースDB接続失敗: {e}")
        
        if item_db_id:
            try:
                database = client.databases.retrieve(database_id=item_db_id)
                print(f"✅ アイテムDB接続成功: {database['title'][0]['text']['content']}")
            except Exception as e:
                print(f"❌ アイテムDB接続失敗: {e}")
        
        return True
        
    except ImportError:
        print("❌ notion-clientパッケージがインストールされていません")
        print("💡 pip install notion-client を実行してください")
        return False
    except Exception as e:
        print(f"❌ Notion接続エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_notion_connection()
    if success:
        print("\n🎉 Notionデータベース接続テスト完了！")
    else:
        print("\n💥 Notionデータベース接続に問題があります")
        sys.exit(1)