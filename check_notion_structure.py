#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notionデータベースの実際のプロパティ構造を確認するスクリプト
"""

import os
import sys
from notion_client import Client
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# Notion APIキーの設定
notion_api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
if not notion_api_key:
    print("❌ Notion APIキーが設定されていません")
    print("💡 .envファイルにNOTION_API_KEYを設定してください")
    sys.exit(1)

# Notionクライアントの初期化
client = Client(auth=notion_api_key)

def check_database_structure(db_id, db_name):
    """データベースの構造を確認"""
    try:
        print(f"\n🔍 {db_name}の構造を確認中...")
        print(f"📊 データベースID: {db_id}")
        
        # データベースの情報を取得
        database = client.databases.retrieve(database_id=db_id)
        
        print(f"\n📋 プロパティ一覧:")
        print("-" * 50)
        
        for prop_name, prop_info in database["properties"].items():
            prop_type = prop_info["type"]
            print(f"• {prop_name}: {prop_type}")
            
            # プロパティの詳細情報を表示
            if prop_type == "select":
                options = prop_info.get("select", {}).get("options", [])
                if options:
                    print(f"  選択肢: {[opt['name'] for opt in options]}")
            elif prop_type == "multi_select":
                options = prop_info.get("multi_select", {}).get("options", [])
                if options:
                    print(f"  選択肢: {[opt['name'] for opt in options]}")
        
        return database["properties"]
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return None

def main():
    """メイン処理"""
    print("🚐 Notionデータベースの構造確認を開始します...")
    print("=" * 60)
    
    # 環境変数からデータベースIDを取得
    databases = {
        "診断ノード": os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID"),
        "修理ケース": os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID"),
        "部品・工具": os.getenv("ITEM_DB_ID")
    }
    
    all_properties = {}
    
    for db_name, db_id in databases.items():
        if db_id:
            properties = check_database_structure(db_id, db_name)
            if properties:
                all_properties[db_name] = properties
        else:
            print(f"\n❌ {db_name}のデータベースIDが設定されていません")
    
    # 結果の要約
    print(f"\n{'='*60}")
    print("📊 確認結果の要約")
    print(f"{'='*60}")
    
    for db_name, properties in all_properties.items():
        print(f"\n🔍 {db_name}:")
        for prop_name, prop_info in properties.items():
            print(f"  • {prop_name}: {prop_info['type']}")
    
    print(f"\n💡 この情報を基に、スクリプトのプロパティ名を修正してください。")

if __name__ == "__main__":
    main()