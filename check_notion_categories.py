#!/usr/bin/env python3
"""
Notionデータベースのカテゴリ設定を詳細確認
"""

import os
from notion_client import Client
from dotenv import load_dotenv

# .envファイルを読み込み
if os.path.exists('.env'):
    load_dotenv()

def check_notion_categories():
    """Notionデータベースのカテゴリ設定を確認"""
    print("🔍 Notionデータベースのカテゴリ設定確認")
    print("=" * 60)
    
    try:
        api_key = os.getenv("NOTION_API_KEY")
        node_db_id = os.getenv("NODE_DB_ID")
        
        if not api_key or not node_db_id:
            print("❌ 環境変数が設定されていません")
            return
        
        client = Client(auth=api_key)
        response = client.databases.query(database_id=node_db_id)
        nodes = response.get("results", [])
        
        print(f"✅ 診断ノード総数: {len(nodes)}件")
        
        # カテゴリ別の集計
        categories = {}
        start_nodes = {}
        end_nodes = {}
        
        for node in nodes:
            properties = node.get("properties", {})
            
            # カテゴリを取得
            category_prop = properties.get("カテゴリ", {})
            category = ""
            if category_prop.get("type") == "rich_text":
                rich_text_content = category_prop.get("rich_text", [])
                if rich_text_content:
                    category = rich_text_content[0].get("plain_text", "")
            
            # 開始フラグを確認
            is_start = properties.get("開始フラグ", {}).get("checkbox", False)
            is_end = properties.get("終端フラグ", {}).get("checkbox", False)
            
            # ノードIDを取得
            node_id_prop = properties.get("ノードID", {})
            node_id = ""
            if node_id_prop.get("type") == "title":
                title_content = node_id_prop.get("title", [])
                if title_content:
                    node_id = title_content[0].get("plain_text", "")
            
            if category:
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
                
                if is_start:
                    start_nodes[category] = node_id
                
                if is_end:
                    if category not in end_nodes:
                        end_nodes[category] = 0
                    end_nodes[category] += 1
        
        print(f"\n📊 カテゴリ別ノード数:")
        for category, count in sorted(categories.items()):
            start_info = "✅" if category in start_nodes else "❌"
            end_info = f"({end_nodes.get(category, 0)}件の終端ノード)" if category in end_nodes else "(終端ノードなし)"
            print(f"  {start_info} {category}: {count}件 {end_info}")
        
        print(f"\n🚀 開始ノード設定済みカテゴリ: {len(start_nodes)}件")
        for category, node_id in start_nodes.items():
            print(f"  - {category}: {node_id}")
        
        print(f"\n⚠️ 問題のあるカテゴリ:")
        for category, count in categories.items():
            if category not in start_nodes:
                print(f"  ❌ {category}: 開始ノードが設定されていません")
            if category not in end_nodes:
                print(f"  ❌ {category}: 終端ノードが設定されていません")
        
        # 推奨カテゴリの確認
        recommended_categories = [
            "バッテリー", "エアコン", "電装系", "タイヤ", "エンジン", 
            "ブレーキ", "サスペンション", "ボディ", "内装", "給排水"
        ]
        
        print(f"\n📋 推奨カテゴリの設定状況:")
        for rec_cat in recommended_categories:
            if rec_cat in categories:
                status = "✅ 設定済み"
            else:
                status = "❌ 未設定"
            print(f"  {status} {rec_cat}")
        
        # 診断フローの完全性チェック
        print(f"\n🔍 診断フローの完全性チェック:")
        complete_categories = 0
        for category in categories:
            if category in start_nodes and category in end_nodes:
                complete_categories += 1
                print(f"  ✅ {category}: 完全な診断フロー")
            else:
                print(f"  ❌ {category}: 不完全な診断フロー")
        
        print(f"\n📈 診断フロー完成度: {complete_categories}/{len(categories)} ({complete_categories/len(categories)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    check_notion_categories()
