#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修理ケースデータベースの詳細な構造を確認するスクリプト
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

# データベースIDの設定
case_db_id = os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID")
if not case_db_id:
    print("❌ 修理ケースデータベースIDが設定されていません")
    print("💡 .envファイルにCASE_DB_IDを設定してください")
    sys.exit(1)

# Notionクライアントの初期化
client = Client(auth=notion_api_key)

def check_repair_case_structure():
    """修理ケースデータベースの構造を詳細に確認"""
    try:
        print("🔍 修理ケースデータベースの詳細構造を確認中...")
        print(f"📊 データベースID: {case_db_id}")
        
        # データベースの情報を取得
        database = client.databases.retrieve(database_id=case_db_id)
        
        print(f"\n📋 プロパティ一覧（詳細）:")
        print("=" * 60)
        
        for prop_name, prop_info in database["properties"].items():
            prop_type = prop_info["type"]
            print(f"\n🔍 プロパティ名: {prop_name}")
            print(f"   型: {prop_type}")
            
            # プロパティの詳細情報を表示
            if prop_type == "select":
                options = prop_info.get("select", {}).get("options", [])
                if options:
                    print(f"   選択肢: {[opt['name'] for opt in options]}")
            elif prop_type == "multi_select":
                options = prop_info.get("multi_select", {}).get("options", [])
                if options:
                    print(f"   選択肢: {[opt['name'] for opt in options]}")
            elif prop_type == "relation":
                relation_info = prop_info.get("relation", {})
                if relation_info:
                    print(f"   関連データベースID: {relation_info.get('database_id', '不明')}")
                    print(f"   関連プロパティ: {relation_info.get('single_property', {}).get('synced_property_name', '不明')}")
            elif prop_type == "rich_text":
                print(f"   説明: テキスト入力可能")
            elif prop_type == "title":
                print(f"   説明: タイトル（必須）")
            elif prop_type == "checkbox":
                print(f"   説明: チェックボックス")
            elif prop_type == "number":
                print(f"   説明: 数値入力")
        
        return database["properties"]
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return None

def main():
    """メイン処理"""
    print("🚐 修理ケースデータベースの詳細構造確認を開始します...")
    print("=" * 60)
    
    properties = check_repair_case_structure()
    
    if properties:
        print(f"\n{'='*60}")
        print("📊 確認結果の要約")
        print(f"{'='*60}")
        
        print(f"\n🔍 修理ケースデータベースの構造:")
        for prop_name, prop_info in properties.items():
            print(f"  • {prop_name}: {prop_info['type']}")
        
        print(f"\n💡 この情報を基に、正しいプロパティ名と型を使用してください。")

if __name__ == "__main__":
    main()
