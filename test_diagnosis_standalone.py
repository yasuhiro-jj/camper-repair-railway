#!/usr/bin/env python3
"""
症状診断システムのスタンドアロンテスト
Streamlitを使わずに診断フローをテスト
"""

import os
from notion_client import Client
from dotenv import load_dotenv

# .envファイルを読み込み
if os.path.exists('.env'):
    load_dotenv()

def load_notion_diagnostic_data():
    """Notionから診断データを読み込み"""
    try:
        api_key = os.getenv("NOTION_API_KEY")
        node_db_id = os.getenv("NODE_DB_ID")
        
        if not api_key or not node_db_id:
            print("❌ 環境変数が設定されていません")
            return None
        
        client = Client(auth=api_key)
        response = client.databases.query(database_id=node_db_id)
        nodes = response.get("results", [])
        
        # データを変換
        diagnostic_nodes = {}
        start_nodes = {}
        
        for node in nodes:
            properties = node.get("properties", {})
            
            # ノードIDを取得
            node_id_prop = properties.get("ノードID", {})
            node_id = ""
            if node_id_prop.get("type") == "title":
                title_content = node_id_prop.get("title", [])
                if title_content:
                    node_id = title_content[0].get("plain_text", "")
            
            if not node_id:
                continue
            
            # 各プロパティを取得
            question_prop = properties.get("質問内容", {})
            question = ""
            if question_prop.get("type") == "rich_text":
                rich_text_content = question_prop.get("rich_text", [])
                if rich_text_content:
                    question = rich_text_content[0].get("plain_text", "")
            
            result_prop = properties.get("診断結果", {})
            result = ""
            if result_prop.get("type") == "rich_text":
                rich_text_content = result_prop.get("rich_text", [])
                if rich_text_content:
                    result = rich_text_content[0].get("plain_text", "")
            
            category_prop = properties.get("カテゴリ", {})
            category = ""
            if category_prop.get("type") == "rich_text":
                rich_text_content = category_prop.get("rich_text", [])
                if rich_text_content:
                    category = rich_text_content[0].get("plain_text", "")
            
            is_start = properties.get("開始フラグ", {}).get("checkbox", False)
            is_end = properties.get("終端フラグ", {}).get("checkbox", False)
            
            next_nodes_prop = properties.get("次のノード", {})
            next_nodes = []
            if next_nodes_prop.get("type") == "rich_text":
                rich_text_content = next_nodes_prop.get("rich_text", [])
                if rich_text_content:
                    next_nodes_text = rich_text_content[0].get("plain_text", "")
                    next_nodes = [node.strip() for node in next_nodes_text.split(",") if node.strip()]
            
            # ノードデータを作成
            node_data = {
                "question": question,
                "category": category,
                "is_start": is_start,
                "is_end": is_end,
                "next_nodes": next_nodes,
                "result": result
            }
            
            diagnostic_nodes[node_id] = node_data
            
            # 開始ノードを記録
            if is_start:
                start_nodes[category] = node_id
        
        return {
            "diagnostic_nodes": diagnostic_nodes,
            "start_nodes": start_nodes
        }
        
    except Exception as e:
        print(f"❌ Notionからの診断データ読み込みに失敗: {e}")
        return None

def simulate_diagnosis_flow(diagnostic_data):
    """診断フローをシミュレート"""
    if not diagnostic_data:
        print("❌ 診断データが読み込めませんでした")
        return
    
    diagnostic_nodes = diagnostic_data["diagnostic_nodes"]
    start_nodes = diagnostic_data["start_nodes"]
    
    print("🔍 症状診断システム - シミュレーション")
    print("=" * 50)
    
    # 利用可能なカテゴリを表示
    available_categories = list(start_nodes.keys())
    print(f"\n📋 利用可能な診断カテゴリ: {len(available_categories)}件")
    for i, category in enumerate(available_categories[:5], 1):  # 最初の5件を表示
        print(f"  {i}. {category}")
    
    # 利用可能なカテゴリから最初のものを選択
    target_category = available_categories[0] if available_categories else None
    
    if not target_category:
        print("⚠️ 利用可能なカテゴリがありません")
        return
    
    print(f"\n🎯 選択されたカテゴリ: {target_category}")
    
    # 診断フローを開始
    current_node_id = start_nodes[target_category]
    print(f"📍 開始ノード: {current_node_id}")
    
    # 診断フローをシミュレート（最大5ステップ）
    for step in range(5):
        current_node = diagnostic_nodes.get(current_node_id)
        if not current_node:
            print(f"❌ ノードが見つかりません: {current_node_id}")
            break
        
        question = current_node.get("question", "")
        if question:
            print(f"\n❓ 質問 {step + 1}: {question}")
        
        # 終端ノードの場合
        if current_node.get("is_end", False):
            result = current_node.get("result", "")
            if result:
                print(f"\n## 🔍 診断結果")
                
                # 診断名の抽出
                diagnosis_lines = result.split('\n')
                diagnosis_name = diagnosis_lines[0] if diagnosis_lines else "症状診断"
                
                # 確信度の計算
                confidence = min(95, max(60, len(result) // 10 + 60))
                
                # 緊急度の判定
                urgency_keywords = ["緊急", "危険", "即座", "停止", "故障"]
                urgency = "緊急" if any(keyword in result for keyword in urgency_keywords) else "要注意"
                
                print(f"診断名: {diagnosis_name}")
                print(f"確信度: {confidence}%")
                print(f"緊急度: {urgency}")
                
                # 診断結果の詳細
                print(f"\n📋 診断詳細:")
                print(result)
                
                # 費用目安の表示
                print(f"\n💰 費用目安:")
                category = current_node.get("category", "")
                default_costs = {
                    "バッテリー": "部品代: 15,000-25,000円\n工賃: 5,000-10,000円\n合計: 20,000-35,000円",
                    "エアコン": "部品代: 30,000-80,000円\n工賃: 15,000-30,000円\n合計: 45,000-110,000円",
                    "電装系": "部品代: 5,000-20,000円\n工賃: 3,000-8,000円\n合計: 8,000-28,000円",
                    "タイヤ": "部品代: 20,000-40,000円\n工賃: 2,000-5,000円\n合計: 22,000-45,000円"
                }
                default_cost = default_costs.get(category, "部品代: 10,000-30,000円\n工賃: 5,000-15,000円\n合計: 15,000-45,000円")
                print(default_cost)
            
            print(f"\n✅ 診断完了!")
            break
        
        # 次のノードへの選択肢
        next_nodes = current_node.get("next_nodes", [])
        if len(next_nodes) >= 2:
            print(f"選択肢: [はい] [いいえ]")
            # シミュレーション: 「はい」を選択
            current_node_id = next_nodes[0]
            print(f"→ 「はい」を選択")
        else:
            print(f"❌ 次のノードが設定されていません")
            break

def main():
    """メイン関数"""
    print("🔧 症状診断システム - スタンドアロンテスト")
    print("=" * 60)
    
    # 診断データを読み込み
    diagnostic_data = load_notion_diagnostic_data()
    
    if diagnostic_data:
        print("✅ 診断データの読み込みに成功")
        print(f"📊 診断ノード数: {len(diagnostic_data['diagnostic_nodes'])}件")
        print(f"🚀 開始ノード数: {len(diagnostic_data['start_nodes'])}件")
        
        # 診断フローをシミュレート
        simulate_diagnosis_flow(diagnostic_data)
    else:
        print("❌ 診断データの読み込みに失敗")

if __name__ == "__main__":
    main()
