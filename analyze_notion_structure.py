#!/usr/bin/env python3
"""
Notionデータベースの構造を詳しく分析
"""

import os
from notion_client import Client
from dotenv import load_dotenv

# .envファイルを読み込み
if os.path.exists('.env'):
    load_dotenv()

def analyze_notion_structure():
    """Notionデータベースの構造を詳しく分析"""
    print("🔍 Notionデータベースの構造分析")
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
        
        # 全プロパティの確認
        if nodes:
            first_node = nodes[0]
            properties = first_node.get("properties", {})
            print(f"\n📋 利用可能なプロパティ:")
            for prop_name, prop_data in properties.items():
                prop_type = prop_data.get("type", "unknown")
                print(f"  - {prop_name}: {prop_type}")
        
        # カテゴリの詳細分析
        categories = {}
        start_nodes = {}
        end_nodes = {}
        
        for node in nodes:
            properties = node.get("properties", {})
            
            # ノードIDを取得
            node_id_prop = properties.get("ノードID", {})
            node_id = ""
            if node_id_prop.get("type") == "title":
                title_content = node_id_prop.get("title", [])
                if title_content:
                    node_id = title_content[0].get("plain_text", "")
            
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
            
            # 質問内容を取得
            question_prop = properties.get("質問内容", {})
            question = ""
            if question_prop.get("type") == "rich_text":
                rich_text_content = question_prop.get("rich_text", [])
                if rich_text_content:
                    question = rich_text_content[0].get("plain_text", "")
            
            if category:
                if category not in categories:
                    categories[category] = []
                categories[category].append({
                    "node_id": node_id,
                    "question": question,
                    "is_start": is_start,
                    "is_end": is_end
                })
                
                if is_start:
                    start_nodes[category] = node_id
                
                if is_end:
                    if category not in end_nodes:
                        end_nodes[category] = []
                    end_nodes[category].append(node_id)
        
        print(f"\n📊 カテゴリ別の詳細分析:")
        for category, nodes_list in categories.items():
            start_count = sum(1 for node in nodes_list if node["is_start"])
            end_count = sum(1 for node in nodes_list if node["is_end"])
            total_count = len(nodes_list)
            
            print(f"\n🔸 {category}:")
            print(f"  - 総ノード数: {total_count}件")
            print(f"  - 開始ノード: {start_count}件")
            print(f"  - 終端ノード: {end_count}件")
            
            # 開始ノードの詳細
            if start_count > 0:
                start_node_list = [node for node in nodes_list if node["is_start"]]
                for start_node in start_node_list:
                    print(f"    📍 開始ノード: {start_node['node_id']}")
                    if start_node['question']:
                        print(f"      質問: {start_node['question'][:50]}...")
            
            # 終端ノードの詳細
            if end_count > 0:
                end_node_list = [node for node in nodes_list if node["is_end"]]
                for end_node in end_node_list[:3]:  # 最初の3件を表示
                    print(f"    🎯 終端ノード: {end_node['node_id']}")
                    if end_node['question']:
                        print(f"      質問: {end_node['question'][:50]}...")
        
        # ノードIDのパターン分析
        print(f"\n🔍 ノードIDのパターン分析:")
        node_id_patterns = {}
        for node in nodes:
            properties = node.get("properties", {})
            node_id_prop = properties.get("ノードID", {})
            node_id = ""
            if node_id_prop.get("type") == "title":
                title_content = node_id_prop.get("title", [])
                if title_content:
                    node_id = title_content[0].get("plain_text", "")
            
            if node_id:
                # ノードIDの最初の部分でパターンを分析
                prefix = node_id.split('_')[0] if '_' in node_id else node_id
                if prefix not in node_id_patterns:
                    node_id_patterns[prefix] = 0
                node_id_patterns[prefix] += 1
        
        for prefix, count in sorted(node_id_patterns.items()):
            print(f"  - {prefix}: {count}件")
        
        # 推奨カテゴリとのマッピング
        print(f"\n📋 推奨カテゴリとのマッピング:")
        recommended_mappings = {
            "waterpump": "給排水",
            "refrigerator": "エアコン",
            "inverter": "電装系",
            "PFC": "電装系",
            "total": "総合",
            "battery": "バッテリー",
            "tire": "タイヤ",
            "engine": "エンジン",
            "brake": "ブレーキ",
            "suspension": "サスペンション",
            "body": "ボディ",
            "interior": "内装"
        }
        
        for prefix, recommended_category in recommended_mappings.items():
            if prefix in node_id_patterns:
                print(f"  ✅ {prefix} → {recommended_category}: {node_id_patterns[prefix]}件")
            else:
                print(f"  ❌ {prefix} → {recommended_category}: 0件")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    analyze_notion_structure()
