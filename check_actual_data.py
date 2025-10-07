#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
実際のNotionデータベースの内容を確認するスクリプト
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

def check_database_content(db_id, db_name):
    """データベースの内容を確認"""
    try:
        print(f"\n🔍 {db_name}の内容を確認中...")
        print(f"📊 データベースID: {db_id}")
        
        # データベースの情報を取得
        database = client.databases.retrieve(database_id=db_id)
        
        print(f"\n📋 データベース名: {database.get('title', [{}])[0].get('plain_text', '不明')}")
        print(f"📊 プロパティ数: {len(database.get('properties', {}))}")
        
        # データベースの内容をクエリ
        response = client.databases.query(database_id=db_id)
        pages = response.get("results", [])
        
        print(f"📝 ページ数: {len(pages)}")
        
        if pages:
            print(f"\n📄 最初の3件の内容:")
            print("-" * 60)
            
            for i, page in enumerate(pages[:3], 1):
                print(f"\n🔍 ページ {i}:")
                properties = page.get("properties", {})
                
                for prop_name, prop_info in properties.items():
                    prop_type = prop_info.get("type", "不明")
                    
                    if prop_type == "title":
                        title_content = prop_info.get("title", [])
                        if title_content:
                            print(f"  • {prop_name}: {title_content[0].get('plain_text', '')}")
                    elif prop_type == "rich_text":
                        rich_text_content = prop_info.get("rich_text", [])
                        if rich_text_content:
                            print(f"  • {prop_name}: {rich_text_content[0].get('plain_text', '')}")
                    elif prop_type == "select":
                        select_content = prop_info.get("select", {})
                        if select_content:
                            print(f"  • {prop_name}: {select_content.get('name', '')}")
                    elif prop_type == "multi_select":
                        multi_select_content = prop_info.get("multi_select", [])
                        if multi_select_content:
                            values = [item.get('name', '') for item in multi_select_content]
                            print(f"  • {prop_name}: {', '.join(values)}")
                    elif prop_type == "relation":
                        relation_content = prop_info.get("relation", [])
                        if relation_content:
                            print(f"  • {prop_name}: {len(relation_content)}件の関連")
                    elif prop_type == "checkbox":
                        checkbox_content = prop_info.get("checkbox", False)
                        print(f"  • {prop_name}: {checkbox_content}")
                    elif prop_type == "number":
                        number_content = prop_info.get("number", 0)
                        print(f"  • {prop_name}: {number_content}")
                    else:
                        print(f"  • {prop_name}: {prop_type}型 - 内容確認不可")
        
        return pages
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return None

def main():
    """メイン処理"""
    print("🚐 実際のNotionデータベースの内容確認を開始します...")
    print("=" * 60)
    
    # 環境変数からデータベースIDを取得
    databases = {
        "診断ノード": os.getenv("NODE_DB_ID") or os.getenv("NOTION_DIAGNOSTIC_DB_ID"),
        "修理ケース": os.getenv("CASE_DB_ID") or os.getenv("NOTION_REPAIR_CASE_DB_ID"),
        "部品・工具": os.getenv("ITEM_DB_ID")
    }
    
    all_pages = {}
    
    for db_name, db_id in databases.items():
        if db_id:
            pages = check_database_content(db_id, db_name)
            if pages:
                all_pages[db_name] = pages
        else:
            print(f"\n❌ {db_name}のデータベースIDが設定されていません")
    
    # 結果の要約
    print(f"\n{'='*60}")
    print("📊 確認結果の要約")
    print(f"{'='*60}")
    
    for db_name, pages in all_pages.items():
        print(f"\n🔍 {db_name}: {len(pages)}件のページ")
    
    print(f"\n💡 この情報を基に、アプリで表示される情報と比較してください。")

if __name__ == "__main__":
    main()
