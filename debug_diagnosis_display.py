#!/usr/bin/env python3
"""
症状診断表示のデバッグスクリプト
"""

import os
from notion_client import Client
from dotenv import load_dotenv

# .envファイルを読み込み
if os.path.exists('.env'):
    load_dotenv()

def debug_diagnosis_display():
    """症状診断の表示をデバッグ"""
    print("🔍 症状診断表示デバッグ")
    print("=" * 50)
    
    # 環境変数の確認
    api_key = os.getenv("NOTION_API_KEY")
    node_db_id = os.getenv("NODE_DB_ID")
    
    if not api_key or not node_db_id:
        print("❌ 環境変数が設定されていません")
        return
    
    try:
        client = Client(auth=api_key)
        response = client.databases.query(database_id=node_db_id)
        nodes = response.get("results", [])
        
        print(f"✅ 診断ノード数: {len(nodes)}件")
        
        # 終端ノード（診断結果）を確認
        end_nodes = []
        for node in nodes:
            properties = node.get("properties", {})
            is_end = properties.get("終端フラグ", {}).get("checkbox", False)
            if is_end:
                # ノードIDを取得
                node_id_prop = properties.get("ノードID", {})
                node_id = ""
                if node_id_prop.get("type") == "title":
                    title_content = node_id_prop.get("title", [])
                    if title_content:
                        node_id = title_content[0].get("plain_text", "")
                
                # 診断結果を取得
                result_prop = properties.get("診断結果", {})
                result = ""
                if result_prop.get("type") == "rich_text":
                    rich_text_content = result_prop.get("rich_text", [])
                    if rich_text_content:
                        result = rich_text_content[0].get("plain_text", "")
                
                # カテゴリを取得
                category_prop = properties.get("カテゴリ", {})
                category = ""
                if category_prop.get("type") == "rich_text":
                    rich_text_content = category_prop.get("rich_text", [])
                    if rich_text_content:
                        category = rich_text_content[0].get("plain_text", "")
                
                end_nodes.append({
                    "node_id": node_id,
                    "result": result,
                    "category": category
                })
        
        print(f"\n📋 終端ノード（診断結果）: {len(end_nodes)}件")
        
        for i, node in enumerate(end_nodes[:3]):  # 最初の3件を表示
            print(f"\n--- 終端ノード {i+1} ---")
            print(f"ノードID: {node['node_id']}")
            print(f"カテゴリ: {node['category']}")
            print(f"診断結果: {node['result'][:100]}...")
            
            # 診断結果の分析
            if node['result']:
                lines = node['result'].split('\n')
                diagnosis_name = lines[0] if lines else "症状診断"
                confidence = min(95, max(60, len(node['result']) // 10 + 60))
                
                urgency_keywords = ["緊急", "危険", "即座", "停止", "故障"]
                urgency = "緊急" if any(keyword in node['result'] for keyword in urgency_keywords) else "要注意"
                
                print(f"抽出された診断名: {diagnosis_name}")
                print(f"計算された確信度: {confidence}%")
                print(f"判定された緊急度: {urgency}")
                
                # 費用目安の確認
                category = node['category']
                default_costs = {
                    "バッテリー": "部品代: 15,000-25,000円\n工賃: 5,000-10,000円\n合計: 20,000-35,000円",
                    "エアコン": "部品代: 30,000-80,000円\n工賃: 15,000-30,000円\n合計: 45,000-110,000円",
                    "電装系": "部品代: 5,000-20,000円\n工賃: 3,000-8,000円\n合計: 8,000-28,000円",
                    "タイヤ": "部品代: 20,000-40,000円\n工賃: 2,000-5,000円\n合計: 22,000-45,000円"
                }
                default_cost = default_costs.get(category, "部品代: 10,000-30,000円\n工賃: 5,000-15,000円\n合計: 15,000-45,000円")
                print(f"カテゴリ別費用目安: {default_cost}")
            else:
                print("❌ 診断結果が空です")
        
        print(f"\n📊 診断結果の表示テスト")
        print("改善された診断結果の表示が正しく動作するかテストします...")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    debug_diagnosis_display()
